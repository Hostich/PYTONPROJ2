from sqlite3 import connect,Row

database:str = "db/school.db"

def getprocess(sql:str,vals:list)->list:
    data: list = []
    try:
        conn: any = connect(database)
        conn.row_factory = Row
        cursor: any = conn.cursor()
        cursor.execute(sql, vals)
        rows = cursor.fetchall()
        data = [dict(row) for row in rows]  # <-- convert to dict
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()
    return data
    
def postprocess(sql:str,vals:list)->bool:
    try:
        conn = connect(database)
        cursor = conn.cursor()
        cursor.execute(sql, vals)
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        conn.rollback()
        print(f"Database error: {e}")
        return False
    finally:
        cursor.close()
        conn.close()
    return True if cursor.rowcount>0 else False
    
    
def addrecord(table:str,**kwargs)->bool:
    keys:list = list(kwargs.keys())
    vals:list = list(kwargs.values())
    qmark:list = ['?']*len(keys)
    flds:str = ",".join(qmark)
    fields:str = ",".join(keys)
    sql:str = f"INSERT INTO {table} ({fields}) VALUES({flds})"
    return postprocess(sql,vals)
    
def getrecord(table:str,**kwargs)->list:
    if kwargs:
        keys = list(kwargs.keys())
        vals = list(kwargs.values())
        flds = " AND ".join([f"{key}=?" for key in keys])
        sql = f"SELECT * FROM {table} WHERE {flds}"
        return getprocess(sql, vals)
    else:
        return getall(table)
        
def getall(table:str)->list:
    sql:str = f"SELECT * FROM {table}"
    return getprocess(sql,[])
    
def deleterecord(table:str,**kwargs)->bool:
    keys:list = list(kwargs.keys())
    vals:list = list(kwargs.values())
    fields:list = []
    for key in keys:
        fields.append(f"{key}=?")
    flds:str = " AND ".join(fields)
    sql:str = f"DELETE FROM {table} WHERE {flds}"
    return postprocess(sql, vals)

def updaterecord(table:str, **kwargs)->bool:
    key:list = list(kwargs.keys())
    vals:list = list(kwargs.values())
    newvals:list = []
    fields = []
    for index in range(1, len(key)):
        fields.append(f"{key[index]}=?")
        newvals.append(f"{vals[index]}")
    flds:str = ",".join(fields)
    sql:str = f"UPDATE {table} SET {flds} WHERE {key[0]}={vals[0]}"
    return postprocess(sql,newvals)