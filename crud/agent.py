from sqlalchemy.orm import Session
from typing import List, Optional
import models
import schemas.agent as agent_schemas

class AgentCRUD:
    @staticmethod
    def create_agent(db: Session, agent_data: agent_schemas.AgentCreate) -> models.Agent:
        """Create a new agent"""
        db_agent = models.Agent(**agent_data.dict())
        db.add(db_agent)
        db.commit()
        db.refresh(db_agent)
        return db_agent
    
    @staticmethod
    def get_agent_by_id(db: Session, agent_id: int) -> Optional[models.Agent]:
        """Get agent by ID"""
        return db.query(models.Agent).filter(models.Agent.id == agent_id).first()
    
    @staticmethod
    def get_agent_by_name(db: Session, name: str) -> Optional[models.Agent]:
        """Get agent by name"""
        return db.query(models.Agent).filter(models.Agent.name == name).first()
    
    @staticmethod
    def get_all_agents(db: Session, skip: int = 0, limit: int = 100) -> List[models.Agent]:
        """Get all agents with pagination"""
        return db.query(models.Agent).filter(models.Agent.is_active == True).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_agent(db: Session, agent_id: int, agent_data: agent_schemas.AgentUpdate) -> Optional[models.Agent]:
        """Update an agent"""
        db_agent = AgentCRUD.get_agent_by_id(db, agent_id)
        if not db_agent:
            return None
        
        update_data = agent_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_agent, field, value)
        
        db.commit()
        db.refresh(db_agent)
        return db_agent
    
    @staticmethod
    def delete_agent(db: Session, agent_id: int) -> bool:
        """Delete an agent (soft delete by setting is_active to False)"""
        db_agent = AgentCRUD.get_agent_by_id(db, agent_id)
        if not db_agent:
            return False
        
        db_agent.is_active = False
        db.commit()
        return True
    
    @staticmethod
    def get_active_agents(db: Session) -> List[models.Agent]:
        """Get all active agents"""
        return db.query(models.Agent).filter(models.Agent.is_active == True).all()
    
    @staticmethod
    def get_agent_count(db: Session) -> int:
        """Get total count of active agents"""
        return db.query(models.Agent).filter(models.Agent.is_active == True).count()
