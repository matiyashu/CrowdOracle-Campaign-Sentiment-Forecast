"""
Ontology generation service.
Step 1: Analyses document text and produces entity/relationship type definitions
suited for social-media opinion simulation.
"""

import logging
import re
from typing import Dict, Any, List, Optional
from ..utils.llm_client import LLMClient
from ..utils.locale import get_language_instruction

logger = logging.getLogger(__name__)


def _to_pascal_case(name: str) -> str:
    """Convert any name format to PascalCase (e.g. 'works_for' → 'WorksFor', 'person' → 'Person')."""
    # Split on non-alphanumeric characters
    parts = re.split(r'[^a-zA-Z0-9]+', name)
    # Then split on camelCase boundaries (e.g. 'camelCase' -> ['camel', 'Case'])
    words = []
    for part in parts:
        words.extend(re.sub(r'([a-z])([A-Z])', r'\1_\2', part).split('_'))
    # Capitalize first letter of each word, drop empties
    result = ''.join(word.capitalize() for word in words if word)
    return result if result else 'Unknown'


# System prompt used when generating ontologies
ONTOLOGY_SYSTEM_PROMPT = """You are an expert knowledge-graph ontology designer. Your task is to analyse the provided text and simulation requirements, then design entity types and relationship types suited for **social-media opinion simulation**.

**IMPORTANT: Output valid JSON only. Do not include any other text.**

## Core context

We are building a **social-media opinion simulation system** in which:
- Every entity is an account or actor that can post, interact, and spread information on social media.
- Entities influence each other through replies, retweets, comments, and responses.
- We need to simulate how various parties react and how information propagates during an opinion event.

Therefore, **entities must be real-world actors who can speak and interact on social media**:

**Allowed**:
- Specific individuals (public figures, key persons, opinion leaders, experts, ordinary people)
- Companies and businesses (including their official accounts)
- Organisations (universities, associations, NGOs, unions, etc.)
- Government departments and regulators
- Media outlets (newspapers, TV stations, blogs, news websites)
- Social-media platforms themselves
- Community representatives (alumni groups, fan clubs, advocacy groups, etc.)

**Not allowed**:
- Abstract concepts (e.g. "public opinion", "sentiment", "trends")
- Topics or themes (e.g. "academic integrity", "education reform")
- Stances or attitudes (e.g. "supporters", "opponents")

## Output format

Output a single JSON object with this structure:

```json
{
    "entity_types": [
        {
            "name": "EntityTypeName (English, PascalCase)",
            "description": "Short description (English, max 100 chars)",
            "attributes": [
                {
                    "name": "attribute_name (English, snake_case)",
                    "type": "text",
                    "description": "Attribute description"
                }
            ],
            "examples": ["Example entity 1", "Example entity 2"]
        }
    ],
    "edge_types": [
        {
            "name": "RELATIONSHIP_NAME (English, UPPER_SNAKE_CASE)",
            "description": "Short description (English, max 100 chars)",
            "source_targets": [
                {"source": "SourceEntityType", "target": "TargetEntityType"}
            ],
            "attributes": []
        }
    ],
    "analysis_summary": "Brief analysis of the text content"
}
```

## Design guidelines (CRITICAL)

### 1. Entity types — strict requirements

**Count: exactly 10 entity types**

**Hierarchy requirement (must include both specific and fallback types)**:

Your 10 entity types must follow this structure:

A. **Fallback types (required, placed last in the list)**:
   - `Person`: Fallback for any individual not covered by a more specific person type.
   - `Organization`: Fallback for any organisation not covered by a more specific organisation type.

B. **Specific types (8 types, derived from the document content)**:
   - Design concrete types for the main actors appearing in the text.
   - Example for an academic incident: `Student`, `Professor`, `University`
   - Example for a business incident: `Company`, `CEO`, `Employee`

**Why fallback types are needed**:
- Text may mention minor actors ("a local teacher", "an anonymous commenter") without a dedicated type.
- If no specific type matches, they should fall into `Person`.
- Similarly, small groups and ad-hoc bodies should fall into `Organization`.

**Principles for specific types**:
- Identify high-frequency or key actor roles in the text.
- Each specific type must have clear boundaries that distinguish it from the fallback type.
- The description must clearly state how this type differs from `Person` or `Organization`.

### 2. Relationship types

- Count: 6–10 types
- Relationships should reflect real social-media interactions.
- Ensure source_targets cover the entity types you have defined.

### 3. Attribute design

- 1–3 key attributes per entity type.
- **Reserved names — do not use**: `name`, `uuid`, `group_id`, `created_at`, `summary`.
- Recommended alternatives: `full_name`, `title`, `role`, `position`, `location`, `description`.

## Entity type reference

**Specific person types**:
- Student, Professor, Journalist, Celebrity, Executive, Official, Lawyer, Doctor

**Person fallback**:
- Person: Any individual not fitting a more specific person type.

**Specific organisation types**:
- University, Company, GovernmentAgency, MediaOutlet, Hospital, School, NGO

**Organization fallback**:
- Organization: Any organisation not fitting a more specific organisation type.

## Relationship type reference

- WORKS_FOR, STUDIES_AT, AFFILIATED_WITH, REPRESENTS, REGULATES,
  REPORTS_ON, COMMENTS_ON, RESPONDS_TO, SUPPORTS, OPPOSES,
  COLLABORATES_WITH, COMPETES_WITH
"""


class OntologyGenerator:
    """
    Ontology generator — analyses document text and produces entity/relationship type definitions.
    """

    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm_client = llm_client or LLMClient()

    def generate(
        self,
        document_texts: List[str],
        simulation_requirement: str,
        additional_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate an ontology definition from document text.

        Args:
            document_texts: List of document texts
            simulation_requirement: Natural-language description of the simulation goal
            additional_context: Optional extra context

        Returns:
            Ontology dict (entity_types, edge_types, analysis_summary)
        """
        # Build the user message
        user_message = self._build_user_message(
            document_texts,
            simulation_requirement,
            additional_context
        )

        lang_instruction = get_language_instruction()
        system_prompt = f"{ONTOLOGY_SYSTEM_PROMPT}\n\n{lang_instruction}\nIMPORTANT: Entity type names MUST be in English PascalCase (e.g., 'PersonEntity', 'MediaOrganization'). Relationship type names MUST be in English UPPER_SNAKE_CASE (e.g., 'WORKS_FOR'). Attribute names MUST be in English snake_case. Only description fields and analysis_summary should use the specified language above."
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]

        # Call LLM
        result = self.llm_client.chat_json(
            messages=messages,
            temperature=0.3,
            max_tokens=4096
        )

        # Validate and post-process the result
        result = self._validate_and_process(result)

        return result

    # Maximum text length passed to the LLM (50 000 characters)
    MAX_TEXT_LENGTH_FOR_LLM = 50000
    
    def _build_user_message(
        self,
        document_texts: List[str],
        simulation_requirement: str,
        additional_context: Optional[str]
    ) -> str:
        """Build the user message sent to the LLM."""

        # Merge all document texts
        combined_text = "\n\n---\n\n".join(document_texts)
        original_length = len(combined_text)

        # Truncate if over 50 000 chars (only affects LLM input, not graph build)
        if len(combined_text) > self.MAX_TEXT_LENGTH_FOR_LLM:
            combined_text = combined_text[:self.MAX_TEXT_LENGTH_FOR_LLM]
            combined_text += (
                f"\n\n...(original text was {original_length} chars; "
                f"truncated to first {self.MAX_TEXT_LENGTH_FOR_LLM} chars for ontology analysis)..."
            )

        message = f"""## Simulation Requirements

{simulation_requirement}

## Document Content

{combined_text}
"""

        if additional_context:
            message += f"""
## Additional Notes

{additional_context}
"""

        message += """
Based on the above, design entity types and relationship types suited for social opinion simulation.

**Rules you must follow**:
1. Output exactly 10 entity types.
2. The last 2 must be the fallback types: Person (individual fallback) and Organization (organisation fallback).
3. The first 8 are specific types derived from the text content.
4. All entity types must be real-world actors capable of posting on social media — no abstract concepts.
5. Attribute names must not use reserved words (name, uuid, group_id, etc.); use full_name, org_name, etc. instead.
"""

        return message
    
    def _validate_and_process(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and post-process the raw LLM result."""

        # Ensure required top-level keys exist
        if "entity_types" not in result:
            result["entity_types"] = []
        if "edge_types" not in result:
            result["edge_types"] = []
        if "analysis_summary" not in result:
            result["analysis_summary"] = ""

        # Validate entity types.
        # Track original → PascalCase name mapping to fix edge source_targets references later.
        entity_name_map = {}
        for entity in result["entity_types"]:
            # Force entity names to PascalCase (Zep API requirement)
            if "name" in entity:
                original_name = entity["name"]
                entity["name"] = _to_pascal_case(original_name)
                if entity["name"] != original_name:
                    logger.warning(f"Entity type name '{original_name}' auto-converted to '{entity['name']}'")
                entity_name_map[original_name] = entity["name"]
            if "attributes" not in entity:
                entity["attributes"] = []
            if "examples" not in entity:
                entity["examples"] = []
            # Enforce 100-char description limit
            if len(entity.get("description", "")) > 100:
                entity["description"] = entity["description"][:97] + "..."

        # Validate edge types
        for edge in result["edge_types"]:
            # Force edge names to SCREAMING_SNAKE_CASE (Zep API requirement)
            if "name" in edge:
                original_name = edge["name"]
                edge["name"] = original_name.upper()
                if edge["name"] != original_name:
                    logger.warning(f"Edge type name '{original_name}' auto-converted to '{edge['name']}'")
            # Fix source_targets references to match PascalCase entity names
            for st in edge.get("source_targets", []):
                if st.get("source") in entity_name_map:
                    st["source"] = entity_name_map[st["source"]]
                if st.get("target") in entity_name_map:
                    st["target"] = entity_name_map[st["target"]]
            if "source_targets" not in edge:
                edge["source_targets"] = []
            if "attributes" not in edge:
                edge["attributes"] = []
            if len(edge.get("description", "")) > 100:
                edge["description"] = edge["description"][:97] + "..."

        # Zep API limits: max 10 custom entity types, max 10 custom edge types
        MAX_ENTITY_TYPES = 10
        MAX_EDGE_TYPES = 10

        # Deduplicate by name, keeping first occurrence
        seen_names = set()
        deduped = []
        for entity in result["entity_types"]:
            name = entity.get("name", "")
            if name and name not in seen_names:
                seen_names.add(name)
                deduped.append(entity)
            elif name in seen_names:
                logger.warning(f"Duplicate entity type '{name}' removed during validation")
        result["entity_types"] = deduped

        # Fallback type definitions
        person_fallback = {
            "name": "Person",
            "description": "Any individual person not fitting other specific person types.",
            "attributes": [
                {"name": "full_name", "type": "text", "description": "Full name of the person"},
                {"name": "role", "type": "text", "description": "Role or occupation"}
            ],
            "examples": ["ordinary citizen", "anonymous netizen"]
        }
        
        organization_fallback = {
            "name": "Organization",
            "description": "Any organization not fitting other specific organization types.",
            "attributes": [
                {"name": "org_name", "type": "text", "description": "Name of the organization"},
                {"name": "org_type", "type": "text", "description": "Type of organization"}
            ],
            "examples": ["small business", "community group"]
        }
        
        # Check which fallback types are already present
        entity_names = {e["name"] for e in result["entity_types"]}
        has_person = "Person" in entity_names
        has_organization = "Organization" in entity_names

        # Collect missing fallback types
        fallbacks_to_add = []
        if not has_person:
            fallbacks_to_add.append(person_fallback)
        if not has_organization:
            fallbacks_to_add.append(organization_fallback)

        if fallbacks_to_add:
            current_count = len(result["entity_types"])
            needed_slots = len(fallbacks_to_add)

            # If adding fallbacks would exceed the limit, trim from the end
            # (preserve the more important specific types at the front)
            if current_count + needed_slots > MAX_ENTITY_TYPES:
                to_remove = current_count + needed_slots - MAX_ENTITY_TYPES
                result["entity_types"] = result["entity_types"][:-to_remove]

            result["entity_types"].extend(fallbacks_to_add)

        # Defensive cap — ensure we never exceed API limits
        if len(result["entity_types"]) > MAX_ENTITY_TYPES:
            result["entity_types"] = result["entity_types"][:MAX_ENTITY_TYPES]

        if len(result["edge_types"]) > MAX_EDGE_TYPES:
            result["edge_types"] = result["edge_types"][:MAX_EDGE_TYPES]

        return result
    
    def generate_python_code(self, ontology: Dict[str, Any]) -> str:
        """
        Render the ontology definition as Python source code.

        Args:
            ontology: Ontology definition dict

        Returns:
            Python source code string
        """
        code_lines = [
            '"""',
            'Custom entity and relationship type definitions.',
            'Auto-generated by BigBrother for social opinion simulation.',
            '"""',
            '',
            'from pydantic import Field',
            'from zep_cloud.external_clients.ontology import EntityModel, EntityText, EdgeModel',
            '',
            '',
            '# ============== Entity Types ==============',
            '',
        ]

        # Generate entity type classes
        for entity in ontology.get("entity_types", []):
            name = entity["name"]
            desc = entity.get("description", f"A {name} entity.")

            code_lines.append(f'class {name}(EntityModel):')
            code_lines.append(f'    """{desc}"""')

            attrs = entity.get("attributes", [])
            if attrs:
                for attr in attrs:
                    attr_name = attr["name"]
                    attr_desc = attr.get("description", attr_name)
                    code_lines.append(f'    {attr_name}: EntityText = Field(')
                    code_lines.append(f'        description="{attr_desc}",')
                    code_lines.append(f'        default=None')
                    code_lines.append(f'    )')
            else:
                code_lines.append('    pass')

            code_lines.append('')
            code_lines.append('')

        code_lines.append('# ============== Relationship Types ==============')
        code_lines.append('')

        # Generate edge type classes
        for edge in ontology.get("edge_types", []):
            name = edge["name"]
            # Convert UPPER_SNAKE_CASE to PascalCase for the class name
            class_name = ''.join(word.capitalize() for word in name.split('_'))
            desc = edge.get("description", f"A {name} relationship.")

            code_lines.append(f'class {class_name}(EdgeModel):')
            code_lines.append(f'    """{desc}"""')

            attrs = edge.get("attributes", [])
            if attrs:
                for attr in attrs:
                    attr_name = attr["name"]
                    attr_desc = attr.get("description", attr_name)
                    code_lines.append(f'    {attr_name}: EntityText = Field(')
                    code_lines.append(f'        description="{attr_desc}",')
                    code_lines.append(f'        default=None')
                    code_lines.append(f'    )')
            else:
                code_lines.append('    pass')

            code_lines.append('')
            code_lines.append('')

        # Generate type registry dicts
        code_lines.append('# ============== Type Configuration ==============')
        code_lines.append('')
        code_lines.append('ENTITY_TYPES = {')
        for entity in ontology.get("entity_types", []):
            name = entity["name"]
            code_lines.append(f'    "{name}": {name},')
        code_lines.append('}')
        code_lines.append('')
        code_lines.append('EDGE_TYPES = {')
        for edge in ontology.get("edge_types", []):
            name = edge["name"]
            class_name = ''.join(word.capitalize() for word in name.split('_'))
            code_lines.append(f'    "{name}": {class_name},')
        code_lines.append('}')
        code_lines.append('')

        # Generate edge source_targets mapping
        code_lines.append('EDGE_SOURCE_TARGETS = {')
        for edge in ontology.get("edge_types", []):
            name = edge["name"]
            source_targets = edge.get("source_targets", [])
            if source_targets:
                st_list = ', '.join([
                    f'{{"source": "{st.get("source", "Entity")}", "target": "{st.get("target", "Entity")}"}}'
                    for st in source_targets
                ])
                code_lines.append(f'    "{name}": [{st_list}],')
        code_lines.append('}')

        return '\n'.join(code_lines)

