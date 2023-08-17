from fastapi import FastAPI 
from .routers import  users ,auth , search ,jobs
from fastapi.middleware.cors import CORSMiddleware

# models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.include_router(posts.router)
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(search.router)
app.include_router(jobs.router)
# app.include_router(votes.router)


@app.get("/")
async def root():
    return {"message": "Hello World"}

