import argparse
from PIL import Image,ImageEnhance
from bs4 import BeautifulSoup
#from BeautifulSoup import BeautifulStoneSoup
import requests
from io import BytesIO
import urllib
import pytesseract
import urllib.request
import getpass
from prettytable import PrettyTable

parser = argparse.ArgumentParser(description='Web crawler for NCTU class schedule') 
parser.add_argument("username",help='username of NCTU portal') 
args = parser.parse_args() 


headers = { 'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36', }

#url = "https://portal.nctu.edu.tw/portal/chkpas.php?"

img_src="https://portal.nctu.edu.tw/captcha/pic.php"#identified picture url
passwd = getpass.getpass("Please input password: ")

while True:

	session = requests.Session()
	session.headers.update(headers)
	response = session.get(img_src)

	image = Image.open(BytesIO(response.content))
	img_grey = image.convert('L')#convert to grey

	brightness =ImageEnhance.Brightness(img_grey)
	bright_img =brightness.enhance(1.5)

	contrast =ImageEnhance.Contrast(bright_img)
	contrast_img =contrast.enhance(2.0)

	contrast_img.save("after.jpg")
	image_after=Image.open('after.jpg')
	number2 = pytesseract.image_to_string(image_after)
	#print ("The captcha is:%s" % number2)

	#number=input()

	#passwd = getpass.getpass("Please input password: ")

	payload = {
    	'username': args.username ,
    	'password': passwd,
    	'pwdtype' :  'static' ,
    	'seccode' :  number2
	}
	 

	result = session.post('https://portal.nctu.edu.tw/portal/chkpas.php?', data = payload, headers = headers)
	if result.url=='https://portal.nctu.edu.tw/LifeRay/PortalMain.php':
		break
#print(result.url)


#url='https://portal.nctu.edu.tw/LifeRay/PortalMain.php'

#result = session.get(url)

#rel=session.get('https://portal.nctu.edu.tw/portallink/link.php?c=5&v_flog=1',headers=headers)
#rel.encoding='utf-8'
#print(rel.text)
rel1=session.get('https://portal.nctu.edu.tw/portal/relay.php?D=cos',headers=headers)
rel1.encoding='utf-8'
#print(rel1.text)


web = session.get('https://portal.nctu.edu.tw/portal/relay.php?D=cos',headers=headers)
soup_data = BeautifulSoup(web.text,"lxml")

s=soup_data.find("input",{"id":"s"})
t=soup_data.find("input",{"id":"t"})
time=soup_data.find("input",{"id":"txtTimestamp"})
jwt=soup_data.find("input",{"id":"jwt"})

data={}
for element in soup_data.find_all("input"):
	data[element.get('id')]=element.get('value')

#print(data)


data['Chk_SSO']='on'
'''data = {
'txtId':'',
'txtPw':'MjY0Nzc2OTc3NjI2MTY1Nw==',
'ldapDN':'cn=0656539,ou=06,ou=student,o=nctu',
'idno':'MTczNzk2ZjdhNjM2YTZhN2M2NzY=',
's':s['value'],
't':t['value'],
'txtTimestamp':time['value'],
'hashKey':'8892c63f6b0d612be17dbcbdbe7de5fc128638a5a59d59e108dc53d769bcc627',
'jwt':jwt['value'],
'Chk_SSO':'on',
'Button1':'登入',
}'''

rel2=session.post('https://course.nctu.edu.tw/jwt.asp',data=data,headers=headers)
rel2.encoding='big5'
#print(rel2.text)

mail={
'ActionToDo':'$UPDATE$DB',
'UpdateEmail':'Y',
'SetPreceptor':'Y',
'EMail':'wlly409@gmail.com',
'ExtTelInSch':'1313',
'ContactTel':'0987514591'
}

rel3=session.post('https://course.nctu.edu.tw/index.asp',data=mail,headers=headers)
rel3.encoding='big5'
#print(rel3.text)

rel4=session.get('https://course.nctu.edu.tw/adSchedule.asp',headers=headers)
rel4.encoding='big5'
schedule=BeautifulSoup(rel4.text,'lxml')
with open("table.text", 'w') as myfile:
	myfile.write(schedule.text)

week=schedule.findAll("table")
#print(week[1])
aList=[]
bList=[]
cList=[]
bigList=[]
big2List=[]
td=week[1].findAll('td',{"class":"dayOfWeek"})
for i in td:
	aList.append(i.getText().strip())
	#print(i.getText().strip())
td1=week[1].findAll('td',{'class':'liststyle1'})
count=0
for j in td1:
	bList.append(j.getText().replace('&nbsp','').replace('\r','').replace('\t','').replace('\n','').strip())
	count+=1
	if count==9:
		bigList.append(bList)
		count=0
		bList=[]
	#print(repr(j.getText().replace('&nbsp','').replace('\r','').replace('\t','').replace('\n','').strip()))
td2=week[1].findAll('td',{'class':'liststyle2'})
for z in td2:
	cList.append(z.getText().replace('&nbsp','').replace('\r','').replace('\t','').replace('\n','').strip())
	count+=1
	if count==9:
		big2List.append(cList)
		count=0
		cList=[]

rel4.encoding='big5'


x = PrettyTable()

x.field_names = aList
for row in range(8):
	x.add_row(bigList[row])
	x.add_row(big2List[row])

print(x)
