import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlmodel import Session, select
from src.infrastructure.db.engine import engine
from src.infrastructure.db.models import GradeScale

def add_ps_scale():
    print("Starting Grade Scale Update...")
    with Session(engine) as session:
        # 1. Update 'P' to start at 50.01
        statement = select(GradeScale).where(GradeScale.scale_name == "Standard").where(GradeScale.grade == "P")
        results = session.exec(statement).all()
        
        for p_scale in results:
            print(f"Updating P scale (ID: {p_scale.id}) min_mark from {p_scale.min_mark} to 50.01")
            p_scale.min_mark = 50.01
            session.add(p_scale)
            
        # 2. Add PS scale if not exists
        statement_ps = select(GradeScale).where(GradeScale.scale_name == "Standard").where(GradeScale.grade == "PS")
        ps_scale = session.exec(statement_ps).first()
        
        if not ps_scale:
            print("Creating PS scale...")
            ps_scale = GradeScale(
                scale_name="Standard",
                grade="PS",
                label="Pass Supplementary",
                min_mark=50.0,
                gpa_point=2.0
            )
            session.add(ps_scale)
        else:
            print(f"Updating PS scale (ID: {ps_scale.id}) gpa_point to 2.0")
            ps_scale.gpa_point = 2.0
            session.add(ps_scale)
            
        session.commit()
        print("Database updated successfully.")

if __name__ == "__main__":
    add_ps_scale()
