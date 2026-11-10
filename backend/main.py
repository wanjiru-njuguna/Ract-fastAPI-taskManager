from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from uuid import UUID, uuid4

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["http://localhost:5137"],
    allow_credentials = False,
    allow_methods = ["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers = ["Content_Type"],
)

# models for the app.We need one to create tasks, update tasks, and delete tasks.

class CreateTask (BaseModel):
    title: str = Field(min_length = 1)

class UpdateTask (BaseModel):
    title : str | None = Field (default = None, min_length = 1)
    completed : bool | None = None

class Task(BaseModel):
    id : UUID = Field(default_factory = uuid4)
    title : str
    completed : bool = False

#temporary storage for the task before connecting it to the database
tasks: dict[UUID, Task] = {}
# next_id : 1

# api endpoint to retrieve all the tasks
@app.get("/tasks", response_model = list[Task])
def get_tasks ():
    return list(tasks.values())

# create a  new task
@app.post("/tasks", response_model = Task, status_code = 201)
def create_task (task:CreateTask ):
    new_task = Task(
        title = task.title,
    )
    tasks[new_task.id] = new_task
    return new_task
# patch :update a task
@app.patch("/tasks/{task_id}", response_model = Task)
def Update_task (task_id :UUID, update :UpdateTask):
    if task_id not in tasks:
        raise HTTPException(
            status_code = 404,
            detail = "Task not found."
        )
    existing_task = tasks[task_id]
    #extract only the fields provided by client
    update_data = update.model_dump(exclude_unset = True)
    # create a new updated object with the update data
    updated_task = existing_task.model_copy(update = update_data)
    # save the updated task to the dictionary
    tasks[task_id] = updated_task
    return updated_task
# removing the task using the delete method
@app.delete("/delete/{task_id}", status_code = 204)
def delete_task (task_id : UUID):
    if task_id not in tasks:
        raise HTTPException(
            status_code = 404,
            detail = "Task not found"
        )
    del tasks[task_id]
    return None