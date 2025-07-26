# wfm_queries.py - WFM-specific query templates and data context
"""
Workforce Management Query Templates and Data Context
Based on the actual WFM database structure with 9 collections
"""

from typing import Dict, List, Any
from datetime import datetime, timedelta

class WFMQueryTemplates:
    """Pre-built query templates for common WFM operations"""
    
    # Collection schemas and sample data structure
    COLLECTION_SCHEMAS = {
        "employees": {
            "description": "Employee master data with personal info, employment history, and contact details",
            "key_fields": ["_id", "firstName", "lastName", "peopleSoftId", "badgeId", "type", "addresses", "contacts", "employmentHistory"],
            "sample_query": "Find employees by employment type or badge ID"
        },
        "activities": {
            "description": "Work activity definitions and descriptions",
            "key_fields": ["_id", "name", "description", "startTime", "endTime", "type"],
            "sample_query": "List available work activities"
        },
        "activityTypes": {
            "description": "Categories and types of work activities",
            "key_fields": ["_id", "name", "description", "category"],
            "sample_query": "Show activity type categories"
        },
        "paycodes": {
            "description": "Payroll codes and compensation rules",
            "key_fields": ["_id", "code", "description", "rate", "type"],
            "sample_query": "List payroll codes and rates"
        },
        "itms_wfm_roles": {
            "description": "User roles and permissions in the WFM system",
            "key_fields": ["_id", "roleName", "permissions", "description"],
            "sample_query": "Show user roles and permissions"
        },
        "ITMS_HOLIDAYS_LIST": {
            "description": "Holiday schedules by location with dates and descriptions",
            "key_fields": ["_id", "NAME", "HOL_DATE", "HOL_DESC", "ADDED_BY", "UPDATED_BY"],
            "sample_query": "Find holidays by date range or name"
        },
        "dailyActivities": {
            "description": "Daily work activity tracking and time logs",
            "key_fields": ["_id", "date", "employee", "name", "startTime", "endTime", "status"],
            "sample_query": "Show daily activities for specific dates or employees"
        },
        "itms_wfm_payroll": {
            "description": "Payroll records with hours worked, dates, and counties",
            "key_fields": ["_id", "badgeId", "firstName", "lastName", "county", "date", "hours", "peoplesoftCode"],
            "sample_query": "Analyze payroll by county, date, or employee"
        },
        "itms_wfm_user_roles": {
            "description": "User role assignments and access permissions",
            "key_fields": ["_id", "user_id", "role_id", "assigned_date", "status"],
            "sample_query": "Show user role assignments"
        }
    }
    
    # Employee Management Queries
    EMPLOYEE_QUERIES = {
        "find_by_badge": {
            "description": "Find employee by badge ID",
            "template": "Find employee with badge ID {badge_id}",
            "mongodb_query": {"badgeId": "{badge_id}"}
        },
        "find_by_name": {
            "description": "Find employees by name",
            "template": "Find employees with name containing {name}",
            "mongodb_query": {"$or": [{"firstName": {"$regex": "{name}", "$options": "i"}}, {"lastName": {"$regex": "{name}", "$options": "i"}}]}
        },
        "employees_by_type": {
            "description": "List employees by employment type",
            "template": "Show all {employment_type} employees",
            "mongodb_query": {"type": "{employment_type}"}
        },
        "employee_count_by_type": {
            "description": "Count employees by employment type",
            "template": "Count employees by employment type",
            "aggregation": [
                {"$unwind": "$type"},
                {"$group": {"_id": "$type", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]
        }
    }
    
    # Payroll Analysis Queries
    PAYROLL_QUERIES = {
        "payroll_by_county": {
            "description": "Payroll summary by county",
            "template": "Show payroll summary for {county}",
            "aggregation": [
                {"$match": {"county": "{county}"}},
                {"$group": {
                    "_id": "$county",
                    "total_hours": {"$sum": "$hours"},
                    "total_employees": {"$addToSet": "$badgeId"},
                    "avg_hours": {"$avg": "$hours"}
                }},
                {"$addFields": {"employee_count": {"$size": "$total_employees"}}}
            ]
        },
        "overtime_analysis": {
            "description": "Find employees with overtime (>40 hours)",
            "template": "Find employees with overtime in {date_range}",
            "mongodb_query": {"hours": {"$gt": 40}}
        },
        "payroll_trends": {
            "description": "Payroll trends over time",
            "template": "Show payroll trends for the last {days} days",
            "aggregation": [
                {"$match": {"date": {"$gte": "date_range_start"}}},
                {"$group": {
                    "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$date"}},
                    "total_hours": {"$sum": "$hours"},
                    "employee_count": {"$addToSet": "$badgeId"}
                }},
                {"$sort": {"_id": 1}}
            ]
        },
        "top_counties_by_hours": {
            "description": "Top counties by total hours worked",
            "template": "Show top {limit} counties by total hours worked",
            "aggregation": [
                {"$group": {
                    "_id": "$county",
                    "total_hours": {"$sum": "$hours"},
                    "employee_count": {"$addToSet": "$badgeId"}
                }},
                {"$addFields": {"employee_count": {"$size": "$employee_count"}}},
                {"$sort": {"total_hours": -1}},
                {"$limit": 10}
            ]
        }
    }
    
    # Activity Tracking Queries
    ACTIVITY_QUERIES = {
        "daily_activities": {
            "description": "Daily activities for a specific date",
            "template": "Show all activities for {date}",
            "mongodb_query": {"date": {"$gte": "start_date", "$lt": "end_date"}}
        },
        "employee_activities": {
            "description": "Activities for a specific employee",
            "template": "Show activities for employee {employee_name}",
            "mongodb_query": {"employee.firstName": "{first_name}", "employee.lastName": "{last_name}"}
        },
        "activity_completion_rate": {
            "description": "Activity completion rates",
            "template": "Show activity completion rates",
            "aggregation": [
                {"$group": {
                    "_id": "$status",
                    "count": {"$sum": 1}
                }},
                {"$sort": {"count": -1}}
            ]
        }
    }
    
    # Holiday Management Queries
    HOLIDAY_QUERIES = {
        "upcoming_holidays": {
            "description": "Upcoming holidays in date range",
            "template": "Show holidays in the next {days} days",
            "mongodb_query": {
                "HOL_DATE": {
                    "$gte": "current_date",
                    "$lte": "end_date"
                }
            }
        },
        "holidays_by_month": {
            "description": "Holidays by month and year",
            "template": "Show holidays for {month} {year}",
            "aggregation": [
                {"$match": {
                    "HOL_DATE": {
                        "$gte": "month_start",
                        "$lt": "month_end"
                    }
                }},
                {"$sort": {"HOL_DATE": 1}}
            ]
        }
    }
    
    # Cross-collection Analysis
    ANALYTICS_QUERIES = {
        "workforce_summary": {
            "description": "Complete workforce summary",
            "template": "Generate workforce summary report",
            "collections": ["employees", "itms_wfm_payroll", "dailyActivities"]
        },
        "employee_productivity": {
            "description": "Employee productivity analysis",
            "template": "Analyze productivity for employee {badge_id}",
            "collections": ["employees", "dailyActivities", "itms_wfm_payroll"]
        }
    }
    
    @classmethod
    def get_query_suggestions(cls, user_input: str) -> List[Dict[str, Any]]:
        """Get relevant query suggestions based on user input"""
        suggestions = []
        user_lower = user_input.lower()
        
        # Employee-related suggestions
        if any(word in user_lower for word in ["employee", "staff", "worker", "badge"]):
            suggestions.extend([
                {"category": "Employee Management", "query": "Find employee by badge ID", "template": cls.EMPLOYEE_QUERIES["find_by_badge"]},
                {"category": "Employee Management", "query": "Show employee count by type", "template": cls.EMPLOYEE_QUERIES["employee_count_by_type"]}
            ])
        
        # Payroll-related suggestions
        if any(word in user_lower for word in ["payroll", "hours", "overtime", "county", "pay"]):
            suggestions.extend([
                {"category": "Payroll Analysis", "query": "Top counties by hours", "template": cls.PAYROLL_QUERIES["top_counties_by_hours"]},
                {"category": "Payroll Analysis", "query": "Find overtime employees", "template": cls.PAYROLL_QUERIES["overtime_analysis"]}
            ])
        
        # Activity-related suggestions
        if any(word in user_lower for word in ["activity", "activities", "daily", "task"]):
            suggestions.extend([
                {"category": "Activity Tracking", "query": "Daily activities", "template": cls.ACTIVITY_QUERIES["daily_activities"]},
                {"category": "Activity Tracking", "query": "Activity completion rates", "template": cls.ACTIVITY_QUERIES["activity_completion_rate"]}
            ])
        
        # Holiday-related suggestions
        if any(word in user_lower for word in ["holiday", "holidays", "vacation", "time off"]):
            suggestions.extend([
                {"category": "Holiday Management", "query": "Upcoming holidays", "template": cls.HOLIDAY_QUERIES["upcoming_holidays"]},
                {"category": "Holiday Management", "query": "Holidays by month", "template": cls.HOLIDAY_QUERIES["holidays_by_month"]}
            ])
        
        return suggestions[:5]  # Return top 5 suggestions
    
    @classmethod
    def get_collection_context(cls) -> str:
        """Get formatted context about all collections"""
        context = "WFM Database Collections:\n\n"
        
        context += "MASTER DATA (6 collections):\n"
        for collection in ["employees", "activities", "activityTypes", "paycodes", "itms_wfm_roles", "ITMS_HOLIDAYS_LIST"]:
            schema = cls.COLLECTION_SCHEMAS[collection]
            context += f"• {collection}: {schema['description']}\n"
        
        context += "\nTRANSACTIONAL DATA (3 collections):\n"
        for collection in ["dailyActivities", "itms_wfm_payroll", "itms_wfm_user_roles"]:
            schema = cls.COLLECTION_SCHEMAS[collection]
            context += f"• {collection}: {schema['description']}\n"
        
        return context

# Sample query builders for dynamic queries
class WFMQueryBuilder:
    """Build dynamic MongoDB queries for WFM data"""
    
    @staticmethod
    def build_employee_search(badge_id: str = None, name: str = None, employment_type: str = None) -> Dict[str, Any]:
        """Build employee search query"""
        query = {}
        
        if badge_id:
            query["badgeId"] = badge_id
        if name:
            query["$or"] = [
                {"firstName": {"$regex": name, "$options": "i"}},
                {"lastName": {"$regex": name, "$options": "i"}}
            ]
        if employment_type:
            query["type"] = employment_type
            
        return query
    
    @staticmethod
    def build_payroll_analysis(county: str = None, date_start: str = None, date_end: str = None) -> List[Dict[str, Any]]:
        """Build payroll analysis aggregation"""
        pipeline = []
        
        # Match stage
        match_query = {}
        if county:
            match_query["county"] = county
        if date_start and date_end:
            match_query["date"] = {"$gte": date_start, "$lte": date_end}
        
        if match_query:
            pipeline.append({"$match": match_query})
        
        # Group by county
        pipeline.extend([
            {"$group": {
                "_id": "$county",
                "total_hours": {"$sum": "$hours"},
                "employee_count": {"$addToSet": "$badgeId"},
                "avg_hours": {"$avg": "$hours"},
                "max_hours": {"$max": "$hours"}
            }},
            {"$addFields": {"employee_count": {"$size": "$employee_count"}}},
            {"$sort": {"total_hours": -1}}
        ])
        
        return pipeline
    
    @staticmethod
    def build_date_range_query(days_back: int = 30) -> Dict[str, Any]:
        """Build date range query for recent data"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        return {
            "date": {
                "$gte": start_date.isoformat(),
                "$lte": end_date.isoformat()
            }
        }

# Quick access to common queries
QUICK_QUERIES = {
    "Show all collections": {
        "tool": "list-collections",
        "args": {"database": "wfm_database"}
    },
    "Employee count by type": {
        "tool": "aggregate",
        "args": {
            "database": "wfm_database",
            "collection": "employees",
            "pipeline": WFMQueryTemplates.EMPLOYEE_QUERIES["employee_count_by_type"]["aggregation"]
        }
    },
    "Top 5 counties by hours": {
        "tool": "aggregate", 
        "args": {
            "database": "wfm_database",
            "collection": "itms_wfm_payroll",
            "pipeline": [
                {"$group": {"_id": "$county", "total_hours": {"$sum": "$hours"}}},
                {"$sort": {"total_hours": -1}},
                {"$limit": 5}
            ]
        }
    },
    "Recent payroll entries": {
        "tool": "find",
        "args": {
            "database": "wfm_database", 
            "collection": "itms_wfm_payroll",
            "query": {},
            "limit": 10,
            "sort": {"date": -1}
        }
    },
    "Upcoming holidays": {
        "tool": "find",
        "args": {
            "database": "wfm_database",
            "collection": "ITMS_HOLIDAYS_LIST",
            "query": {"HOL_DATE": {"$gte": datetime.now().isoformat()}},
            "limit": 10,
            "sort": {"HOL_DATE": 1}
        }
    }
}