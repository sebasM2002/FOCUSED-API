from fastapi import APIRouter, FastAPI, Depends, HTTPException, status
from fastapi.security import  OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from database.database import get_db
from models.SqlAlchemy.usuario import Usuario
from datetime import timedelta, datetime
from models.Pydantic.usuario import UsuarioEdit, UsuarioCreate, UsuarioDelete, UsuarioBase, Token
from functions.encrpytion import hash_password as hash_ps ,verify_password as pass_verify, pwd_context, oauth2_scheme, authenticate_user, ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, get_current_user

admin_router = APIRouter(
    prefix="/usuarios",
    tags=["usuarios"]
)

@admin_router.post("/", summary = "Create User")
async def create_admin(usuario: UsuarioCreate, db: AsyncSession = Depends(get_db), current_user: UsuarioCreate = Depends(get_current_user)):
    if(current_user.id_rol != 0):
        raise HTTPException(status_code=404, detail ="You cannot access this functionality.")
    else:
        hashed_password = hash_ps((usuario.password))
        actions = "I"
        new_user = Usuario(nombre=usuario.nombre, email=usuario.email, password=hashed_password, id_rol=usuario.id_rol)

        try:
            await db.execute(
                text("CALL p_usuario_actions(:v_id, :v_actions, :v_nombre, :v_email, :v_password, :v_role)"),
                {
                    "v_id": new_user.id,  
                    "v_actions": actions,
                    "v_nombre": new_user.nombre,
                    "v_email": new_user.email,
                    "v_password": new_user.password,
                    "v_role": new_user.id_rol
                }
            )
            await db.commit()
            return {"message": "User created successfully"}
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

@admin_router.get("/", summary = "Get Users")
async def get_admins(db: AsyncSession = Depends(get_db), current_user: UsuarioCreate = Depends(get_current_user)):
    if(current_user.id_rol != 0):
        raise HTTPException(status_code=404, detail ="You cannot access this functionality.")
    else:
        try:
            result = await db.execute(select(Usuario))
            admin = result.scalars().all()
            
            if not admin:
                raise HTTPException(status_code=404, detail="No user found")
            
            return admin
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

@admin_router.get("/{user_id}", summary = "Get one User by ID")
async def get_admin(user_id: int, db: AsyncSession = Depends(get_db) , current_user: UsuarioCreate = Depends(get_current_user)):
    if(current_user.id_rol != 0):
        raise HTTPException(status_code=404, detail ="You cannot access this functionality.")
    else:
        try:
            result = await db.execute(
                text("SELECT * FROM usuario WHERE id = :user_id"),
                {"user_id": user_id}
            )
            user = result.fetchone()
            
            if not user:
                raise HTTPException(status_code=404, detail="No user found")
            
            return {
                "id": user[0],
                "nombre": user[1],
                "email": user[2], 
                "password": user[3],
                "role": user[4]
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


@admin_router.put("/{user_id}", summary = "Update User")
async def update_admin(usuario:UsuarioEdit, db: AsyncSession = Depends(get_db) , current_user: UsuarioCreate = Depends(get_current_user)):
    if(current_user.id_rol != 0):
        raise HTTPException(status_code=404, detail ="You cannot access this functionality.")
    else:
        try:
            result = await db.execute(
                text("SELECT nombre, email, password, id_rol FROM usuario WHERE id = :user_id"),
                {"user_id": usuario.id}
            )
            current_user = result.fetchone()

            if not current_user:
                raise HTTPException(status_code=404, detail="User not found")

            updated_username = usuario.nombre if usuario.nombre  is not None else current_user.nombre
            updated_email = usuario.email if usuario.email is not None else current_user.email
            hashed_password = hash_ps(usuario.password) if usuario.password else current_user.password
            updated_role = usuario.id_rol if usuario.id_rol is not None else current_user.id_rol

            actions = "U"
            new_user = Usuario(id=usuario.id, nombre=updated_username, email=updated_email, password=hashed_password, id_rol=updated_role)

            await db.execute(
                text("CALL p_usuario_actions(:v_id, :v_actions, :v_nombre, :v_email, :v_password, :v_role)"),
                {
                    "v_id": new_user.id,  
                    "v_actions": actions,
                    "v_nombre": new_user.nombre,
                    "v_email": new_user.email,
                    "v_password": new_user.password,
                    "v_role": new_user.id_rol
                }
            )
            await db.commit()
            return {"message": "User updated successfully"}
        
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    
@admin_router.delete("/{user_id}", summary = "Delete a user")
async def delete_admin(user: UsuarioDelete, db: AsyncSession = Depends(get_db) , current_user: UsuarioCreate = Depends(get_current_user)):
    if(current_user.id_rol != 0):
        raise HTTPException(status_code=404, detail ="You cannot access this functionality.")
    else:
        actions = "D"
        try:
            await db.execute(
                text("CALL p_usuario_actions(:v_id, :v_actions, :v_nombre, :v_email, :v_password, :v_role)"),
                {
                    "v_id": user.id,
                    "v_actions": actions,
                    "v_nombre": " ",
                    "v_email": " ",
                    "v_password": " ",
                    "v_role": 0
                }
            )
            await db.commit()
            return {"message": "User deleted successfully"}
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    
@admin_router.post("/login/", summary = "User LogIn")
async def login(user: UsuarioBase, db: AsyncSession = Depends(get_db)):

    result = await db.execute(
        text("SELECT * FROM usuario WHERE nombre = :nombre"), 
        {
            "nombre": user.nombre
        }
    )
    newUser = result.fetchone()

    if not user:
        raise HTTPException(status_code=400, detail="Invalid username or password")

    hashed_password = newUser.password

    if not pass_verify(user.password, hashed_password):
        raise HTTPException(status_code=400, detail="Invalid username or password")

    return {"msg": "Login successful"}

@admin_router.post("/token/", response_model = Token , summary = "JWT Token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await create_access_token(
        data={"sub": user.nombre}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@admin_router.get("/me/", response_model= UsuarioCreate, summary = "Get User")
async def read_users_me (current_user: UsuarioCreate = Depends(get_current_user)):
    return current_user

@admin_router.get("/me/items/", summary = "Get User Object")
async def read_own_items (current_user: UsuarioCreate = Depends(get_current_user)):
    return [{"item_id": 1, "owner": current_user.nombre}]