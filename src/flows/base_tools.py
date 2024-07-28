from models.base_model import BaseModel

def provide_plan_tool(model):
    return model.make_tool(
        "provide_plan",
        "Provides a plan to the user for accomplishing the task. This will be a numbered list with titles of each step and no other information",
        {"plan": "string"},
        ["plan"]
    )
    
def provide_explanation_tool(model):
    return model.make_tool(
        "provide_explanation",
        "Provides an explanation for a step to the user in an informative manner. Commands should be explained in a way that can be educational for the user. The title should be the step number or name",
        {"title": "string", "explanation": "string"},
        ["explanation"]
    )
    
def provide_resolution_tool(model):
    return model.make_tool(
        "provide_resolution",
        "Used to provide the resolution you will attempt after handling an unexpected output from a step. If the issue is not recoverable, the process will end",
        {"resolution": "string", "recoverable": "boolean"},
        ["resolution"]
    )
    
def provide_command_tool(model):
    return model.make_tool(
        "provide_command",
        "Provides a command to be executed as part of a step, prior to execution, for the user to either ask questions about or approve for execution",
        {"command": "string", "require_sudo": "boolean"},
        ["command", "require_sudo"]
    )

def execute_command_tool(model: BaseModel, can_mark_dangerous=False):
    model.require_supervision = can_mark_dangerous
    params = {"command": "string"}
    reqs = ["command"]
    
    if can_mark_dangerous:
        params["dangerous"] = "boolean"
        reqs.append("dangerous")
    
    return model.make_tool(
        "execute_command",
        "Execute a command in the shell",
        params,
        reqs
    )
    
def end_process_tool(model: BaseModel, include_summary=True, include_details=True):
    params = {"success": "boolean"}
    reqs = ["success"]
    
    if include_summary:
        params["summary"] = "string"
        reqs.append("summary")
        
    if include_details:
        params["details"] = { "type": "string", "description": "Detailed information in markdown syntax about the task's results, if necessary" }
    
    return model.make_tool(
        "end_process",
        "Ends the task, returning control of the terminal to the user",
        params,
        reqs
    )