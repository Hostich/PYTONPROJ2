from dbhelper import addrecord

ok = addrecord("admin", name="Test Admin", email="test@example.com", password="1234")
print(ok)