from plgxgpib import prologixEthernet

con = prologixEthernet("10.20.4.31")
a = input("Enter Command")
while a != "blah":
    con.writeascii(a, escape=False)
    try:
        print(con.readascii())
    except:
        print("No Return")
    a = input("Enter Command: ")
