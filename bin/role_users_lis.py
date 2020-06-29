

def del_run(r,name):
    r.del_All(db=1,name=name)
    r.del_All(db=2,name=name)

def role_run(r,name1,name2,users,lis):
    del_run(r,name1)
    del_run(r,name2)
    r.role(name1,users)
    r.role(name2,lis)
    return '下发任务成功'

def role_tags(r,name,lis,count):
    if count == 'y':del_run(r,name)
    r.role('tags',lis)
    return '下发任务成功'