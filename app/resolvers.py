from ariadne import MutationType, QueryType
from app.models import User, Project, RoleEnum, ProjectMember
from app.database import SessionLocal
from app.auth import hash_password, verify_password, create_token, get_current_user

mutation = MutationType()
query = QueryType()

@mutation.field("register")
def resolve_register(_, info, email, password):
    db = SessionLocal()
    if db.query(User).filter(User.email == email).first():
        raise Exception("User already exists")
    user = User(email=email, password_hash=hash_password(password))
    db.add(user)
    db.commit()
    return {"token": create_token(user.id), "user": user}

@mutation.field("login")
def resolve_login(_, info, email, password):
    db = SessionLocal()
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        raise Exception("Invalid credentials")
    return {"token": create_token(user.id), "user": user}

@query.field("me")
def resolve_me(_, info):
    user_id = get_current_user(info.context["request"])
    if not user_id:
        raise Exception("Not Authenticated")
    db = SessionLocal()
    return db.query(User).get(user_id)

@mutation.field("createProject")
def resolve_create_project(_, info, name):
    user_id = get_current_user(info.context["request"])
    if not user_id:
        raise Exception("Not Authenticated")

    db = SessionLocal()
    project = Project(name=name, owner_id=user_id)
    db.add(project)
    db.commit()
    db.refresh(project)

    member = ProjectMember(user_id=user_id, project_id=project.id, role=RoleEnum.ADMIN)
    db.add(member)
    db.commit()
    return project

    