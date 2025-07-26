# collection_manager.py - WFM Collection Manager for all 9 collections
"""
Collection Manager for Workforce Management Database
Handles all 9 collections: 6 master data + 3 transactional data
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from mcp_connection_manager import MCPConnectionManager
from wfm_queries import WFMQueryTemplates, WFMQueryBuilder, QUICK_QUERIES

class WFMCollectionManager:
    """Manages all WFM collections with intelligent query routing"""
    
    def __init__(self, mcp_client: MCPConnectionManager):
        self.mcp_client = mcp_client
        self.logger = logging.getLogger(__name__)
        
        # Collection categorization
        self.MASTER_COLLECTIONS = [
            "employees", "activities", "activityTypes", 
            "paycodes", "itms_wfm_roles", "ITMS_HOLIDAYS_LIST"
        ]
        
        self.TRANSACTIONAL_COLLECTIONS = [
            "dailyActivities", "itms_wfm_payroll", "itms_wfm_user_roles"
        ]
        
        self.ALL_COLLECTIONS = self.MASTER_COLLECTIONS + self.TRANSACTIONAL_COLLECTIONS
        
        # Collection metadata cache
        self._collection_metadata = {}
        self._schemas_loaded = False
    
    async def initialize(self) -> bool:
        """Initialize the collection manager and load schemas"""
        try:
            await self._load_collection_schemas()
            await self._analyze_collection_stats()
            self._schemas_loaded = True
            self.logger.info("✅ Collection Manager initialized with 9 WFM collections")
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Collection Manager: {e}")
            return False
    
    async def _load_collection_schemas(self):
        """Load schemas for all collections"""
        for collection in self.ALL_COLLECTIONS:
            try:
                schema_result = await self.mcp_client.get_collection_schema(
                    collection=collection,
                    database="wfm_database"
                )
                
                if schema_result.get("success"):
                    self._collection_metadata[collection] = {
                        "schema": schema_result.get("result", {}),
                        "type": "master" if collection in self.MASTER_COLLECTIONS else "transactional",
                        "description": WFMQueryTemplates.COLLECTION_SCHEMAS.get(collection, {}).get("description", ""),
                        "key_fields": WFMQueryTemplates.COLLECTION_SCHEMAS.get(collection, {}).get("key_fields", [])
                    }
                    self.logger.info(f"✅ Loaded schema for {collection}")
                else:
                    self.logger.warning(f"⚠️ Failed to load schema for {collection}")
                    
            except Exception as e:
                self.logger.error(f"❌ Error loading schema for {collection}: {e}")
    
    async def _analyze_collection_stats(self):
        """Analyze statistics for all collections"""
        for collection in self.ALL_COLLECTIONS:
            try:
                count_result = await self.mcp_client.execute_tool(
                    "count",
                    {"database": "wfm_database", "collection": collection}
                )
                
                if count_result.get("success"):
                    # Handle MCP result format - result might be a list of TextContent objects
                    result = count_result.get("result", [])
                    count = 0
                    
                    if isinstance(result, list) and len(result) > 0:
                        # Extract text from first TextContent object
                        first_item = result[0]
                        if hasattr(first_item, 'text'):
                            try:
                                # Parse the text content as JSON to get count
                                data = json.loads(first_item.text)
                                count = data.get("count", 0)
                            except:
                                # Fallback: try to extract number from text
                                import re
                                numbers = re.findall(r'\d+', first_item.text)
                                count = int(numbers[0]) if numbers else 0
                    
                    if collection in self._collection_metadata:
                        self._collection_metadata[collection]["document_count"] = count
                    self.logger.info(f"📊 {collection}: {count} documents")
                    
            except Exception as e:
                self.logger.error(f"❌ Error getting count for {collection}: {e}")
    
    def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """Get comprehensive information about a collection"""
        if collection_name not in self.ALL_COLLECTIONS:
            return {"error": f"Collection {collection_name} not found in WFM database"}
        
        metadata = self._collection_metadata.get(collection_name, {})
        template_info = WFMQueryTemplates.COLLECTION_SCHEMAS.get(collection_name, {})
        
        return {
            "name": collection_name,
            "type": metadata.get("type", "unknown"),
            "description": metadata.get("description", template_info.get("description", "")),
            "key_fields": metadata.get("key_fields", template_info.get("key_fields", [])),
            "document_count": metadata.get("document_count", 0),
            "sample_query": template_info.get("sample_query", ""),
            "schema_available": "schema" in metadata
        }
    
    def get_all_collections_summary(self) -> Dict[str, Any]:
        """Get summary of all collections"""
        summary = {
            "total_collections": len(self.ALL_COLLECTIONS),
            "master_data": {
                "count": len(self.MASTER_COLLECTIONS),
                "collections": []
            },
            "transactional_data": {
                "count": len(self.TRANSACTIONAL_COLLECTIONS),
                "collections": []
            },
            "total_documents": 0
        }
        
        for collection in self.MASTER_COLLECTIONS:
            info = self.get_collection_info(collection)
            summary["master_data"]["collections"].append(info)
            summary["total_documents"] += info.get("document_count", 0)
        
        for collection in self.TRANSACTIONAL_COLLECTIONS:
            info = self.get_collection_info(collection)
            summary["transactional_data"]["collections"].append(info)
            summary["total_documents"] += info.get("document_count", 0)
        
        return summary
    
    async def execute_quick_query(self, query_name: str) -> Dict[str, Any]:
        """Execute a predefined quick query"""
        if query_name not in QUICK_QUERIES:
            return {"error": f"Quick query '{query_name}' not found"}
        
        query_config = QUICK_QUERIES[query_name]
        tool_name = query_config["tool"]
        args = query_config["args"]
        
        try:
            result = await self.mcp_client.execute_tool(tool_name, args)
            return {
                "query_name": query_name,
                "success": result.get("success", False),
                "result": result.get("result"),
                "tool_used": tool_name
            }
        except Exception as e:
            self.logger.error(f"❌ Quick query '{query_name}' failed: {e}")
            return {"error": str(e), "query_name": query_name}
    
    async def find_employees(self, badge_id: str = None, name: str = None, 
                           employment_type: str = None, limit: int = 10) -> Dict[str, Any]:
        """Find employees with various filters"""
        try:
            query = WFMQueryBuilder.build_employee_search(badge_id, name, employment_type)
            
            result = await self.mcp_client.execute_tool(
                "find",
                {
                    "database": "wfm_database",
                    "collection": "employees",
                    "query": query,
                    "limit": limit
                }
            )
            
            return {
                "query_type": "employee_search",
                "filters": {"badge_id": badge_id, "name": name, "employment_type": employment_type},
                "success": result.get("success", False),
                "result": result.get("result"),
                "count": len(result.get("result", [])) if result.get("success") else 0
            }
            
        except Exception as e:
            self.logger.error(f"❌ Employee search failed: {e}")
            return {"error": str(e), "query_type": "employee_search"}
    
    async def analyze_payroll(self, county: str = None, days_back: int = 30) -> Dict[str, Any]:
        """Analyze payroll data with filters"""
        try:
            # Build date range
            date_filter = WFMQueryBuilder.build_date_range_query(days_back)
            
            # Build aggregation pipeline
            pipeline = WFMQueryBuilder.build_payroll_analysis(
                county=county,
                date_start=date_filter["date"]["$gte"],
                date_end=date_filter["date"]["$lte"]
            )
            
            result = await self.mcp_client.execute_tool(
                "aggregate",
                {
                    "database": "wfm_database",
                    "collection": "itms_wfm_payroll",
                    "pipeline": pipeline
                }
            )
            
            return {
                "query_type": "payroll_analysis",
                "filters": {"county": county, "days_back": days_back},
                "success": result.get("success", False),
                "result": result.get("result"),
                "analysis_period": f"Last {days_back} days"
            }
            
        except Exception as e:
            self.logger.error(f"❌ Payroll analysis failed: {e}")
            return {"error": str(e), "query_type": "payroll_analysis"}
    
    async def get_daily_activities(self, date: str = None, employee_badge: str = None, 
                                 limit: int = 20) -> Dict[str, Any]:
        """Get daily activities with filters"""
        try:
            query = {}
            
            if date:
                # Parse date and create range
                target_date = datetime.fromisoformat(date.replace("Z", ""))
                next_date = target_date + timedelta(days=1)
                query["date"] = {
                    "$gte": target_date.isoformat(),
                    "$lt": next_date.isoformat()
                }
            
            if employee_badge:
                query["employee.badgeId"] = employee_badge
            
            result = await self.mcp_client.execute_tool(
                "find",
                {
                    "database": "wfm_database",
                    "collection": "dailyActivities",
                    "query": query,
                    "limit": limit,
                    "sort": {"date": -1}
                }
            )
            
            return {
                "query_type": "daily_activities",
                "filters": {"date": date, "employee_badge": employee_badge},
                "success": result.get("success", False),
                "result": result.get("result"),
                "count": len(result.get("result", [])) if result.get("success") else 0
            }
            
        except Exception as e:
            self.logger.error(f"❌ Daily activities query failed: {e}")
            return {"error": str(e), "query_type": "daily_activities"}
    
    async def get_upcoming_holidays(self, days_ahead: int = 60) -> Dict[str, Any]:
        """Get upcoming holidays"""
        try:
            current_date = datetime.now()
            end_date = current_date + timedelta(days=days_ahead)
            
            # Use MongoDB ISODate format for proper date comparison
            query = {
                "HOL_DATE": {
                    "$gte": {"$date": current_date.isoformat() + "Z"},
                    "$lte": {"$date": end_date.isoformat() + "Z"}
                }
            }
            
            result = await self.mcp_client.execute_tool(
                "find",
                {
                    "database": "wfm_database",
                    "collection": "ITMS_HOLIDAYS_LIST",
                    "query": query,
                    "sort": {"HOL_DATE": 1},
                    "limit": 20
                }
            )
            
            # Process result to extract count from TextContent objects  
            actual_count = 0
            if result.get("success") and result.get("result"):
                result_list = result.get("result", [])
                if isinstance(result_list, list) and len(result_list) > 0:
                    # First item usually contains count info
                    first_item = result_list[0]
                    if hasattr(first_item, 'text'):
                        try:
                            import re
                            count_match = re.search(r'Found (\d+) documents', first_item.text)
                            if count_match:
                                actual_count = int(count_match.group(1))
                        except:
                            actual_count = len(result_list) - 1  # Subtract header
            
            return {
                "query_type": "upcoming_holidays",
                "period": f"Next {days_ahead} days",
                "success": result.get("success", False),
                "result": result.get("result"),
                "count": actual_count
            }
            
        except Exception as e:
            self.logger.error(f"❌ Holidays query failed: {e}")
            return {"error": str(e), "query_type": "upcoming_holidays"}
    
    async def generate_workforce_report(self) -> Dict[str, Any]:
        """Generate comprehensive workforce report"""
        try:
            report = {
                "generated_at": datetime.now().isoformat(),
                "database": "wfm_database",
                "collections_analyzed": len(self.ALL_COLLECTIONS)
            }
            
            # Get collection summary
            collections_summary = self.get_all_collections_summary()
            report["collections"] = collections_summary
            
            # Get employee count by type
            employee_types = await self.mcp_client.execute_tool(
                "aggregate",
                {
                    "database": "wfm_database",
                    "collection": "employees",
                    "pipeline": WFMQueryTemplates.EMPLOYEE_QUERIES["employee_count_by_type"]["aggregation"]
                }
            )
            report["employee_types"] = employee_types.get("result", []) if employee_types.get("success") else []
            
            # Get top counties by hours
            top_counties = await self.mcp_client.execute_tool(
                "aggregate",
                {
                    "database": "wfm_database",
                    "collection": "itms_wfm_payroll",
                    "pipeline": WFMQueryTemplates.PAYROLL_QUERIES["top_counties_by_hours"]["aggregation"]
                }
            )
            report["top_counties"] = top_counties.get("result", []) if top_counties.get("success") else []
            
            # Get recent activity stats
            activity_stats = await self.mcp_client.execute_tool(
                "aggregate",
                {
                    "database": "wfm_database",
                    "collection": "dailyActivities",
                    "pipeline": WFMQueryTemplates.ACTIVITY_QUERIES["activity_completion_rate"]["aggregation"]
                }
            )
            report["activity_stats"] = activity_stats.get("result", []) if activity_stats.get("success") else []
            
            return {
                "query_type": "workforce_report",
                "success": True,
                "result": report
            }
            
        except Exception as e:
            self.logger.error(f"❌ Workforce report generation failed: {e}")
            return {"error": str(e), "query_type": "workforce_report"}
    
    def get_query_suggestions(self, user_input: str) -> List[Dict[str, Any]]:
        """Get query suggestions based on user input"""
        suggestions = WFMQueryTemplates.get_query_suggestions(user_input)
        
        # Add collection-specific suggestions
        user_lower = user_input.lower()
        
        if "collection" in user_lower or "database" in user_lower:
            suggestions.insert(0, {
                "category": "Database Overview",
                "query": "Show all collections",
                "description": "List all 9 WFM collections with statistics"
            })
        
        if "report" in user_lower or "summary" in user_lower:
            suggestions.append({
                "category": "Reporting",
                "query": "Generate workforce report",
                "description": "Comprehensive workforce analytics report"
            })
        
        return suggestions
    
    def is_ready(self) -> bool:
        """Check if collection manager is ready to use"""
        return self._schemas_loaded and len(self._collection_metadata) > 0

# Example usage and testing
async def test_collection_manager():
    """Test the collection manager"""
    from mcp_connection_manager import MCPConnectionManager
    import os
    
    # Initialize MCP client
    mcp_client = MCPConnectionManager(
        connection_string=os.getenv("MONGODB_CONNECTION_STRING", "mongodb://localhost:27017/wfm_database")
    )
    
    if await mcp_client.connect():
        print("✅ MCP client connected")
        
        # Initialize collection manager
        manager = WFMCollectionManager(mcp_client)
        
        if await manager.initialize():
            print("✅ Collection Manager initialized")
            
            # Test collection summary
            summary = manager.get_all_collections_summary()
            print(f"📊 Database summary: {summary['total_collections']} collections, {summary['total_documents']} total documents")
            
            # Test quick query
            result = await manager.execute_quick_query("Employee count by type")
            print(f"👥 Employee types: {result}")
            
            # Test employee search
            employees = await manager.find_employees(name="John")
            print(f"🔍 Found {employees.get('count', 0)} employees named John")
            
            # Test workforce report
            report = await manager.generate_workforce_report()
            print(f"📋 Workforce report generated: {report.get('success', False)}")
            
        else:
            print("❌ Failed to initialize Collection Manager")
    else:
        print("❌ Failed to connect MCP client")

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    
    asyncio.run(test_collection_manager())