from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime
import uuid

Base = declarative_base()

class CreditBalance(Base):
    __tablename__ = "credit_balances"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(String, nullable=False, index=True)
    month_year = Column(String, nullable=False)
    current_balance = Column(Integer, nullable=False)
    monthly_limit = Column(Integer, default=1000)
    total_used_this_month = Column(Integer, default=0)
    total_researches_this_month = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    version = Column(Integer, default=1)
    
    def __repr__(self):
        return f"<CreditBalance(user_id='{self.user_id}', balance={self.current_balance})>"

class CreditTransaction(Base):
    __tablename__ = "credit_transactions"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    transaction_id = Column(String, unique=True, nullable=False)
    balance_id = Column(UUID, nullable=False)  # Foreign key to credit_balances
    amount = Column(Integer, nullable=False)
    balance_after = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=func.now())
    research_request_id = Column(String, index=True)
    research_depth = Column(String)
    
    def __repr__(self):
        return f"<CreditTransaction(transaction_id='{self.transaction_id}', amount={self.amount})>"

class ResearchStats(Base):
    __tablename__ = "research_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True)
    total_researches_this_month = Column(Integer, default=0)
    total_used_this_month = Column(Float, default=0.0)
    average_credits_per_research = Column(Float, default=0.0)
    month_year = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return (f"<ResearchStats(user_id='{self.user_id}', month='{self.month_year}', "
                f"total_researches={self.total_researches_this_month})>")
    
    @property
    def average_credits_per_research_calculated(self):
        return ((self.total_used_this_month / self.total_researches_this_month) 
                if self.total_researches_this_month > 0 else 0)
