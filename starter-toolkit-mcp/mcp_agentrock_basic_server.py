from mcp.server.fastmcp import FastMCP
from starlette.responses import JSONResponse
import boto3
from typing import Dict, List, Any, Optional

mcp = FastMCP(host="0.0.0.0", stateless_http=True)

@mcp.tool()
def add_numbers(a: int, b: int) -> int:
    """Add two numbers together"""
    return a + b

@mcp.tool()
def multiply_numbers(a: int, b: int) -> int:
    """Multiply two numbers together"""
    return a * b

@mcp.tool()
def greet_user(name: str) -> str:
    """Greet a user by name"""
    return f"Hello, {name}! Nice to meet you."

@mcp.tool()
def get_glue_table_schema(
    database_name: str = "b2b-data", 
    table_name: str = "b2b-reports-data-learning_activities", 
    region: str = "eu-west-1"
) -> Dict[str, Any]:
    """
    Extract AWS Glue table schema from specified region.
    
    Args:
        database_name: Name of the Glue database
        table_name: Name of the Glue table
        region: AWS region where the table is located (default: us-east-1)
    
    Returns:
        Dictionary containing table schema information including columns, 
        data types, storage format, and metadata
    """
    try:
        # Create Glue client for the specified region
        glue_client = boto3.client('glue', region_name=region)
        
        # Get table information
        response = glue_client.get_table(
            DatabaseName=database_name,
            Name=table_name
        )
        
        table = response['Table']
        
        # Extract schema information
        schema_info = {
            "database_name": database_name,
            "table_name": table_name,
            "region": region,
            "columns": [],
            "partition_keys": [],
            "storage_descriptor": {},
            "table_properties": {},
            "metadata": {}
        }
        
        # Extract column information
        if 'StorageDescriptor' in table and 'Columns' in table['StorageDescriptor']:
            for column in table['StorageDescriptor']['Columns']:
                column_info = {
                    "name": column.get('Name', ''),
                    "type": column.get('Type', ''),
                    "comment": column.get('Comment', '')
                }
                schema_info["columns"].append(column_info)
        
        # Extract partition keys
        if 'PartitionKeys' in table:
            for partition_key in table['PartitionKeys']:
                partition_info = {
                    "name": partition_key.get('Name', ''),
                    "type": partition_key.get('Type', ''),
                    "comment": partition_key.get('Comment', '')
                }
                schema_info["partition_keys"].append(partition_info)
        
        # Extract storage descriptor information
        if 'StorageDescriptor' in table:
            storage_desc = table['StorageDescriptor']
            schema_info["storage_descriptor"] = {
                "location": storage_desc.get('Location', ''),
                "input_format": storage_desc.get('InputFormat', ''),
                "output_format": storage_desc.get('OutputFormat', ''),
                "serde_info": {
                    "serialization_library": storage_desc.get('SerdeInfo', {}).get('SerializationLibrary', ''),
                    "parameters": storage_desc.get('SerdeInfo', {}).get('Parameters', {})
                },
                "compressed": storage_desc.get('Compressed', False),
                "parameters": storage_desc.get('Parameters', {})
            }
        
        # Extract table properties and metadata
        schema_info["table_properties"] = table.get('Parameters', {})
        schema_info["metadata"] = {
            "created_by": table.get('CreatedBy', ''),
            "creation_time": table.get('CreateTime').isoformat() if table.get('CreateTime') else '',
            "last_analyzed_time": table.get('LastAnalyzedTime').isoformat() if table.get('LastAnalyzedTime') else '',
            "last_access_time": table.get('LastAccessTime').isoformat() if table.get('LastAccessTime') else '',
            "table_type": table.get('TableType', ''),
            "retention": table.get('Retention', 0)
        }
        
        return schema_info
        
    except Exception as e:
        return {
            "error": f"Failed to extract schema for table {database_name}.{table_name} in region {region}",
            "error_details": str(e),
            "database_name": database_name,
            "table_name": table_name,
            "region": region
        }

@mcp.tool()
def list_glue_tables_in_database(
    database_name: str = "b2b-data", 
    region: str = "eu-west-1",
    max_results: int = 100
) -> Dict[str, Any]:
    """
    List all tables in a specific Glue database within a region.
    
    Args:
        database_name: Name of the Glue database
        region: AWS region where the database is located (default: us-east-1)
        max_results: Maximum number of tables to return (default: 100)
    
    Returns:
        Dictionary containing list of tables with basic information
    """
    try:
        # Create Glue client for the specified region
        glue_client = boto3.client('glue', region_name=region)
        
        # Get tables in the database
        response = glue_client.get_tables(
            DatabaseName=database_name,
            MaxResults=max_results
        )
        
        tables_info = {
            "database_name": database_name,
            "region": region,
            "tables": [],
            "total_tables": len(response.get('TableList', []))
        }
        
        # Extract basic table information
        for table in response.get('TableList', []):
            table_info = {
                "name": table.get('Name', ''),
                "creation_time": table.get('CreateTime').isoformat() if table.get('CreateTime') else '',
                "table_type": table.get('TableType', ''),
                "location": table.get('StorageDescriptor', {}).get('Location', '') if 'StorageDescriptor' in table else '',
                "column_count": len(table.get('StorageDescriptor', {}).get('Columns', [])) if 'StorageDescriptor' in table else 0,
                "partition_key_count": len(table.get('PartitionKeys', []))
            }
            tables_info["tables"].append(table_info)
        
        return tables_info
        
    except Exception as e:
        return {
            "error": f"Failed to list tables in database {database_name} in region {region}",
            "error_details": str(e),
            "database_name": database_name,
            "region": region
        }

if __name__ == "__main__":
    mcp.run(transport="streamable-http")