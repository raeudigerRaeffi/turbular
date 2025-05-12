

Intro_Prompt = f"""You are an expert MySQL data analyst. Your job is to generate an Sql query based upon a question 
about a database and the database structure. The database structure is given to you as a MySQL Create Table 
command for each table in the database. It is highly critical for our business that you manage to fulfill this task.

"""

def default_prompt():
    return ""
def cr_prompt(_db ,_examples ,_question):
    pass
