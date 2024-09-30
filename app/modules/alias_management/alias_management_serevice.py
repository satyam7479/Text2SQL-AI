import traceback
from fastapi import Depends
from sqlalchemy.orm import Session
from app.models.ask_lokaly_alias_model import AskLokalyAlias
from config.database import getDb
from sqlalchemy import or_

class ListAliasesService:
    def listAliases(db: Session = Depends(getDb)):
        try:
            where_conditions = {}
            # Sample conditions for testing
            where_conditions = {
                'table_name': {'like': '%'},
                'column_name': {'like': '%'},
                'alias_name': {'like': '%'}
            }

            # Single query with no `is_included` filter initially
            aliases_query = db.query(AskLokalyAlias).filter(
                or_(
                    AskLokalyAlias.table_name.like(where_conditions.get('table_name', {}).get('like', '')),
                    AskLokalyAlias.column_name.like(where_conditions.get('column_name', {}).get('like', '')),
                    AskLokalyAlias.alias_name.like(where_conditions.get('alias_name', {}).get('like', ''))
                )
            ).order_by(AskLokalyAlias.sequence.asc())

            # Execute the query
            aliases = aliases_query.all()

            COLUMN_MAPPINGS = {}
            COLUMN_PRIORITIES = {}
            VISIBILITY = {}

            # Process aliases for all outputs
            for alias in aliases:
                table_name = alias.table_name
                column_name = alias.column_name
                alias_name = alias.alias_name
                sequence = alias.sequence
                is_included = alias.is_included

                # For COLUMN_MAPPINGS
                if table_name not in COLUMN_MAPPINGS:
                    COLUMN_MAPPINGS[table_name] = {}
                COLUMN_MAPPINGS[table_name][column_name] = alias_name

                # For COLUMN_PRIORITIES
                if table_name not in COLUMN_PRIORITIES:
                    COLUMN_PRIORITIES[table_name] = []
                COLUMN_PRIORITIES[table_name].append((alias_name, sequence))  # Store as tuple

                # For VISIBILITY: Apply `is_included=0` filter
                if is_included == 0:
                    if table_name not in VISIBILITY:
                        VISIBILITY[table_name] = []
                    VISIBILITY[table_name].append(column_name)

            # Sort COLUMN_PRIORITIES by sequence
            for table in COLUMN_PRIORITIES:
                COLUMN_PRIORITIES[table].sort(key=lambda x: x[1])  # Sort by sequence

            return {
                "COLUMN_MAPPINGS": COLUMN_MAPPINGS,
                "COLUMN_PRIORITIES": {table: [name for name, _ in sorted_aliases] for table, sorted_aliases in COLUMN_PRIORITIES.items()},
                "VISIBILITY": VISIBILITY
            }
        except Exception as e:
            traceback_str = traceback.format_exc()
            print(traceback_str)
            line_no = traceback.extract_tb(e.__traceback__)[-1][1]
            print(f"Exception occurred on line {line_no}")
            return {"status": "error", "message": str(e)}
        
    

    