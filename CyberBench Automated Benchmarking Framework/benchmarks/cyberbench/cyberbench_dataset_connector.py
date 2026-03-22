import os
import json
import psycopg2
from typing import List, Dict, Optional
from models.baseprompt import BasePrompt  # adjust import path

class CyberBenchDataSetConnector:
    def __init__(self):
        self.connection = psycopg2.connect(
            dbname=os.getenv("POSTGRES_DB", "db"),
            user=os.getenv("POSTGRES_USER", "postgres"),
            password=os.getenv("POSTGRES_PASSWORD", "postgres"),
            host=os.getenv("POSTGRES_HOST", "db"),
            port=int(os.getenv("POSTGRES_PORT", 5432))
        )

    def close(self):
        self.connection.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def get_templates_by_strategies(self, strategies: List[str]) -> Dict[str, List[Dict]]:
        with self.connection.cursor() as cursor:
            cursor.execute(
                """SELECT id, template, attack_strategy, language 
                   FROM attack_templates 
                   WHERE attack_strategy = ANY(%s)""",
                (strategies,)
            )
            columns = [desc[0] for desc in cursor.description]
            templates = [dict(zip(columns, row)) for row in cursor.fetchall()]

        grouped = {}
        for tpl in templates:
            strat = tpl["attack_strategy"]
            grouped.setdefault(strat, []).append(tpl)

        return grouped

    def get_templates_by_strategy(self, strategy: str) -> List[Dict]:
        with self.connection.cursor() as cursor:
            cursor.execute(
                """SELECT id, template, attack_strategy, language, stage 
                   FROM attack_templates 
                   WHERE attack_strategy = %s""",
                (strategy,)
            )
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def get_base_prompts(
        self,
        source: Optional[str] = None,
        category: Optional[str] = None,
        sample_size: Optional[int] = None
    ) -> List[BasePrompt]:
        query = "SELECT id, source, categories, prompt, prompt_object, prompt_goal FROM base"
        conditions = []
        params = []

        if source:
            conditions.append("source = %s")
            params.append(source)

        if category:
            conditions.append("""
                EXISTS (
                    SELECT 1
                    FROM jsonb_array_elements(categories) arr
                    WHERE arr @> %s::jsonb
                )
            """)
            params.append(json.dumps([category]))

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        if sample_size:
            query += " ORDER BY RANDOM() LIMIT %s"
            params.append(sample_size)

        with self.connection.cursor() as cursor:
            cursor.execute(query, params)
            columns = [desc[0] for desc in cursor.description]
            rows = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return [
            BasePrompt(
                prompt=row.get("prompt", ""),
                prompt_goal=row.get("prompt_goal", ""),
                prompt_object=row.get("prompt_object", ""),
                categories=row.get("categories", "")
            )
            for row in rows
        ]