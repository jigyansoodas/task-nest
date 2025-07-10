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

@query.field("getProjectDetails")
def resolve_get_project_details(_, info, project_id):
    user_id = get_current_user(info.context["request"])
    if not user_id:
        raise Exception("Not Authenticated")
    db = SessionLocal()
    project = db.query(Project).get(project_id)
    if not project:
        raise Exception("Project not found")
    return project

@query.field("getUserDetails")
def resolve_get_project_details(_, info, user_id):
    current_user_id = get_current_user(info.context["request"])
    if not current_user_id:
        raise Exception("Not Authenticated")
    db = SessionLocal()
    user = db.query(User).get(user_id)
    if not user:
        raise Exception("User not found")
    return user

@query.field("listProjectMembers")
def resolve_get_project_details(_, info, project_id):
    current_user_id = get_current_user(info.context["request"])
    if not current_user_id:
        raise Exception("Not Authenticated")
    db = SessionLocal()
    project_members = db.query(ProjectMember).filter(ProjectMember.project_id == project_id)
    if not project_members:
        raise Exception("Project not found")
    return project_members

@mutation.field("inviteUserToProject")
def resolve_invite_user_to_project(_, info, project_id, user_id, role):
    db = info.context["db"]
    current_user = get_current_user(info.context["request"])

    if not current_user:
        raise Exception("Not Authenticated")

    admin_member = db.query(ProjectMember).filter_by(
        project_id=project_id,
        user_id=current_user,
        role=RoleEnum.ADMIN
    ).first()

    if not admin_member:
        raise Exception("Only Admins can invite users to a project")

    new_member = ProjectMember(user_id=user_id, project_id=project_id, role=role)
    db.add(new_member)
    db.commit()
    return True