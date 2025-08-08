from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
import logging
from database import get_db
import models
import schemas.agent as agent_schemas
from crud.agent import AgentCRUD

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/", response_model=agent_schemas.AgentResponse, status_code=status.HTTP_201_CREATED)
def create_agent(
    agent_data: agent_schemas.AgentCreate,
    db: Session = Depends(get_db)
):
    """Create a new agent"""
    try:
        logger.info(f"Creating agent: {agent_data.name}")
        
        # Check if agent with same name already exists
        existing_agent = AgentCRUD.get_agent_by_name(db, agent_data.name)
        if existing_agent:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Agent with this name already exists"
            )
        
        db_agent = AgentCRUD.create_agent(db, agent_data)
        logger.info(f"Agent created successfully: ID {db_agent.id}")
        return db_agent
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating agent: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/", response_model=agent_schemas.AgentListResponse)
def get_agents(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: Session = Depends(get_db)
):
    """Get all active agents"""
    try:
        logger.info(f"Getting agents (skip={skip}, limit={limit})")
        
        agents = AgentCRUD.get_all_agents(db, skip, limit)
        total_count = AgentCRUD.get_agent_count(db)
        
        return agent_schemas.AgentListResponse(
            agents=agents,
            total_count=total_count
        )
        
    except Exception as e:
        logger.error(f"Error getting agents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/{agent_id}", response_model=agent_schemas.AgentResponse)
def get_agent(
    agent_id: int,
    db: Session = Depends(get_db)
):
    """Get agent by ID"""
    try:
        logger.info(f"Getting agent: {agent_id}")
        
        agent = AgentCRUD.get_agent_by_id(db, agent_id)
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agent not found"
            )
        
        return agent
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting agent: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.put("/{agent_id}", response_model=agent_schemas.AgentResponse)
def update_agent(
    agent_id: int,
    agent_data: agent_schemas.AgentUpdate,
    db: Session = Depends(get_db)
):
    """Update an agent"""
    try:
        logger.info(f"Updating agent: {agent_id}")
        
        # Check if agent exists
        existing_agent = AgentCRUD.get_agent_by_id(db, agent_id)
        if not existing_agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agent not found"
            )
        
        # If name is being updated, check for conflicts
        if agent_data.name and agent_data.name != existing_agent.name:
            name_conflict = AgentCRUD.get_agent_by_name(db, agent_data.name)
            if name_conflict:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Agent with this name already exists"
                )
        
        updated_agent = AgentCRUD.update_agent(db, agent_id, agent_data)
        if not updated_agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agent not found"
            )
        
        logger.info(f"Agent updated successfully: ID {agent_id}")
        return updated_agent
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating agent: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_agent(
    agent_id: int,
    db: Session = Depends(get_db)
):
    """Delete an agent (soft delete)"""
    try:
        logger.info(f"Deleting agent: {agent_id}")
        
        success = AgentCRUD.delete_agent(db, agent_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agent not found"
            )
        
        logger.info(f"Agent deleted successfully: ID {agent_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting agent: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/active/list", response_model=List[agent_schemas.AgentResponse])
def get_active_agents(db: Session = Depends(get_db)):
    """Get all active agents (for dropdown/selection)"""
    try:
        logger.info("Getting active agents")
        
        agents = AgentCRUD.get_active_agents(db)
        return agents
        
    except Exception as e:
        logger.error(f"Error getting active agents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )
