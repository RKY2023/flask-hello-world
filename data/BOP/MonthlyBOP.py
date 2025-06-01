from pypdf import PdfReader, PdfWriter
import os
import json
import camelot
# python3 -m pip uninstall camelot
# python3 -m pip uninstall camelot-py
# python3 -m pip install camelot-py[cv]
import pandas as pd
import re
import json
import os
# from dotenv import load_dotenv

# Global Variables
debug =0

# Current Directory
env_directory = os.getcwd()
current_directory = os.path.join(env_directory, 'Projects','My-Expense')
print("The current working directory is:", current_directory)

# Setup json file
file = os.path.join(current_directory, 'setup.json')
f = open(file)
decrpt_keys = json.load(f)

def notepad2data(file, debug):
    text_file = open(file, "r")
    print('File:',file)
    if(debug==1):
        text_file = open("D:\Livings\special case Bank Statements.txt", "r")
    lines = text_file.readlines()
    # print(lines)
    # print(len(lines))
    dateArr=[]
    TransRefArr = []
    ChqRefArr = []
    CreditArr = []
    DebitArr = []
    BalArr = []
    # 'templine' for break in trnsaction id
    templine = ''
    for line_no,line in enumerate(lines):
        if(line_no > 72):
            # print(line)
            line = line.replace('TRANSACTION OVERVIEW','')
            if(templine == ''):
                date = line[:8]
                # print(date)
                # check first 8 char are date or not
                x = re.search("^(0?[1-9]|[12][0-9]|3[01])[\/\-](0?[1-9]|1[012])[\/\-]\d{2}$", date)
                if (x == None):
                    continue

            # check last char are no or not
            x = re.search("\d{1,}\.\d{2}\n", line)
            if ( x == None):
                templine = line
                continue
            else :
                line = templine + line
                # print(line,x)
                templine = ''

            # print(date, x)

            # # to check date format as PDF(DD-MM-YY)
            # dateArr.append(date)
            # to update date format as PDF(YY-MM-DD) into DBMS
            date = '20'+date[6:8]+'-'+date[3:5]+'-'+date[:2]
            dateArr.append(date)
            
            line = line[8:]
            line = line.strip()
            
            # split in texts(transaction id) and numbers(cheque no, credit, debit, balance)
            
            x = line.find('- ')
            # print(x)
            TransRefText = line[:x]
            
            match = " "+line[x:]
            # comment this for check
            match = match.split(' ')
            # print(match, len(match))
            lenchecker = len(match)
            if(len(match)!=5): # case for cheque (len=3) or other cases
                x = re.findall("(\d{1,}\.\d{2})", line) # exclude balance
                # print(line, x)
            
                # exit()
                match= []
                for i in range(5):
                    match.append('0')
                # for xi in x:
                #     for xii in xi:
                #         if(xii == ''):
                #             continue
                #         match += xii
                # match = match.replace('-','- ').replace('  ',' ')
                # match = match.split(' ')
                # print(match, len(match))
                lenchecker = len(match)
                
                # ([-]|[ ])[0-9]*([-]|[ ])*[0-9]*($|\.\d{2})
                # (\d{1,}\.\d{2})|([ ]|[-])
                x1 = re.search("([-]|[ ])[0-9]*([-]|[ ])*[0-9]*($|\.\d{2})", line)
                # print(line, x1)
                
                check_no = line[x1.start():].lstrip().split(' ')[0]
                # print(check_no)
                # exit()
                TransRefText = TransRefText[:x1.start()]
                match[1] = check_no
                match[2] = x[0] # credit
                match[4] = x[1] # balance
                if(len(x) ==2):
                    lenchecker=5
            if(lenchecker != 5):
                print('Error Line:',line,'\n len: ',lenchecker,'\n', x, x1)
                exit()
            numbers = match
            # # numbers = line[x.start():x.end()]
            # # # ChqRefArr.append(numbers)
            # # numbers = ' ' + numbers
            # # numbers = numbers.replace('  ',' ').replace('-','')
            # numbers = numbers.replace('-','')
            # numbers = numbers.split(' ')
            # print(numbers) # numbers[0] is useless as contain extra space for regex
            # if (line_no > 80):
            #     exit()
            TransRefText = TransRefText.strip()
            TransRefArr.append(TransRefText)
            ChqRefArr.append(numbers[1].replace('-',''))
            CreditArr.append(numbers[2].replace('-','0'))
            DebitArr.append(numbers[3].replace('-','0'))
            BalArr.append(numbers[4].replace('-','0'))

    # Transform data into tables
    dt_DF = pd.DataFrame(dateArr)
    tr_DF = pd.DataFrame(TransRefArr)
    ch_DF = pd.DataFrame(ChqRefArr)
    cr_DF = pd.DataFrame(CreditArr)
    db_DF = pd.DataFrame(DebitArr)
    bl_DF = pd.DataFrame(BalArr)
    MainDataFrame = pd.concat([dt_DF, tr_DF, ch_DF, cr_DF, db_DF, bl_DF], axis=1)
    MainDataFrame.columns =['date', 'transactionIdRef', 'chequeRefNo', 'credit', 'debit', 'balance']
    print(MainDataFrame)
    # exit()
    text_file.close()
    return MainDataFrame

def getFilenameWithoutExtension(absSourceFilePath):
    fileAbsPathMeta = {}
    filePathArray = absSourceFilePath.split('\\')
    fileAbsPathMeta['file'] = filePathArray[len(filePathArray)-1]
    fileArray = filePathArray[len(filePathArray)-1].split('.')
    fileAbsPathMeta['filename'] = fileArray[0]
    fileAbsPathMeta['ext'] = fileArray[1]
    fileAbsPathMeta['path'] = absSourceFilePath.replace(fileAbsPathMeta['file'],'')
    return fileAbsPathMeta

def decryptPDF(absSourceFilePath,path):
    filename = getFilenameWithoutExtension(absSourceFilePath)['file']
    try: 
        # reader = PdfReader("encrypted-pdf.pdf")
        reader = PdfReader(absSourceFilePath)
        writer = PdfWriter()

        keyCount = 0
        for key in decrpt_keys['decrpt_keys']:
            if reader.is_encrypted:
                decryptStatus = reader.decrypt(key)
                if decryptStatus == 2: # 2 = success, [0,1] = fail
                    break
            keyCount += 1
            if keyCount == len(decrpt_keys['decrpt_keys']):
                print('New Key Needed! File:', absSourceFilePath)
                exit()
        
        # Add all pages to the writer
        pages= reader.pages
        for page in pages:
            writer.add_page(page)
            exit
        with open(path+"decrypted-"+filename, "wb") as f:
            writer.write(f)
        print('Decrypted:',absSourceFilePath)
        return path+"decrypted-"+filename
        
    except NameError:
        print('Error:', NameError)
    
def pdf2df():
    pd.reset_option("max_columns")
    # extract all the tables in the PDF file
    # abc = camelot.read_pdf("decrypted-pdf.pdf")   #address of file location
    tables = camelot.read_pdf("decrypted-"+file)   #address of file location
    # number of tables extracted
    print("Total tables extracted:", tables.n)

def deleteFile(file):
    try:
        if os.path.exists(file):
            os.remove(file)
        else:
            print("The file does not exist")
        return True
    except NameError:
        return False

def convertPDFtoTXT(absSourceFilename,file_txt):
    global debug
    output = ''
    try:            
        import PyPDF2
        pdfFileObj = open(absSourceFilename, 'rb')
        
        # creating a pdf reader object
        pdfReader = PyPDF2.PdfReader(pdfFileObj)
        
        # printing number of pages in pdf file
        pages = len(pdfReader.pages)
        output += 'Pages: ' + str(pages) +'['
        content = ''
        for t in range(0, pages):
            output += str(t) + ','
            # creating a page object
            pageObj = pdfReader.pages[t]
            
            # extracting text from page
            text = pageObj.extract_text()
            if(debug == 1):
                print(text)
            content = content + text
            # print(pageObj)
            # print(pageObj.images)
        
        # print(fileName)
        output = output[0:-1] +']' 
        with open(file_txt, 'w') as f:
            f.write(content)
        # closing the pdf file object
        pdfFileObj.close()
    # convertPDFtoTXT(file)
    # def croppdf(file):
    # def trAy():
    #     from pdfreader import SimplePDFViewer
    #     fd = open(file, "rb")
    #     viewer = SimplePDFViewer(fd)
    #     print(viewer.render())
    #     markdown = viewer.canvas.text_content
    #     # print(markdown)
    #     print(viewer.canvas.strings)
    except NameError:
        print('Error:', NameError)
        exit()
    finally:
        print('PDF to TXT Done.', output)

def getListofFiles(rootLoc = 'D:\\Livings\\Bank Statements\\pdfs\\', fileTypes = ['.pdf','.txt']):
    result = {}

    for ft in fileTypes:
        result[ft] = []

    for path, subdirs, files in os.walk(rootLoc):
        for name in files:
            absPath = os.path.join(path, name)
            file_name = os.path.basename(absPath)
            file_name_withoutextension = os.path.splitext(file_name)[0]
            for ft in fileTypes:
                fileNam_withType = os.path.join(path,file_name_withoutextension + ft)
                result[ft].append(fileNam_withType)
    return result

def generatefilelocation():
    try:
        rootLoc = rootLoc = 'D:\\Livings\\Bank Statements\\pdfs\\'
        destLoc = 'D:\\Livings\\Bank Statements\\csv\\'
        fileTypes = ['.pdf','.txt']
        filesAndTypesDict = getListofFiles(rootLoc , fileTypes)
        # print(filesAndTypesDict)
        for i,file_pdf in enumerate(filesAndTypesDict['.pdf']):
            file_txt = filesAndTypesDict['.txt'][i]
            # print(i, file_pdf, file_txt)
            decryptedFile = decryptPDF(file_pdf,rootLoc)
            convertPDFtoTXT(decryptedFile,file_txt)
            deleteFile(decryptedFile) # delete decrypted pdf after pdf to txt conversion
            dataframe = notepad2data(file_txt,0)
            filename = getFilenameWithoutExtension(file_txt)['filename']
            dataframe.to_csv(destLoc + filename +'.csv', index=False) 
            deleteFile(file_txt) # delete txt file after txt to csv conversion
    except NameError:
        print('Error:', NameError)
        exit()

def renamePdfByDateDesc():
    try:
        rootLoc = rootLoc = 'D:\\Livings\\Bank Statements\\pdfs\\'
        destLoc = 'D:\\Livings\\Bank Statements\\csv\\'
        fileTypes = ['.pdf','.txt']
        filesAndTypesDict = getListofFiles(rootLoc , fileTypes)
        # print(filesAndTypesDict)
        for i,file_pdf in enumerate(filesAndTypesDict['.pdf']):
            date = file_pdf[-10:-4]
            file = getFilenameWithoutExtension(file_pdf)
            yr = date[4:6]
            mn = date[0:2]
            dt = date[2:4]
            newfilename = file['path'] + '20' + yr + '_' + mn + '_' + dt + '_' + file['filename'][0:-6] + '.' + file['ext']
            # print(newfilename)
            os.rename(file_pdf, newfilename)
            # exit()

    except NameError:
        print('Error:', NameError)
        exit()

def insertDataFrameToDatabase(dataframe):
    import pymysql as ps
    try:
        cn=ps.connect(host='localhost',port=3306,user='root',password='2023',db='sys')
        cmd=cn.cursor()
        for i,row in dataframe.iterrows():
            #here %S means string values 
            sql = "INSERT INTO sys.transactions(date, transaction_id, cheque_ref_no, credit, debit, balance) VALUES (%s,%s,%s,%s,%s,%s)"
            cmd.execute(sql, tuple(row))
            print("Record inserted")
            # the connection is not auto committed by default, so we must commit to save our changes
            cn.commit()
        # query="select * from guild_scrapped"
        
        # cmd.execute(query)
        
        # rows=cmd.fetchall()
        
        # # print(rows)
        # for row in rows:
        #     for col in row:
        #         print(col,end=' ')
        #     print()
        
        cn.close()

    except Exception as e:
        print(e)
    # exit()

def debugSpecialCase():
    notepad2data('', 1)

def autoGUI(option):
    global error, pageURLchanged, firstrun
    # minimizeVSCODE()

    # PART 1 Fetching pdf
    if(option == 1):
        renamePdfByDateDesc()
        
    # PART 2 Get all pdf, Decrypt pdf => Text
    if(option == 2):
        # getListofFiles()
        generatefilelocation()
    
    # PART 3 Text => CSV
    if(option == 3):
        print('')

    # both
    if(option == 4):
        autoGUI(1)
        autoGUI(2)
        autoGUI(3)

    if(option == 5):
        exit()

def autoGUI_main():
    print('Select below option:')
    print('1: Extract Mail')
    print('2: Decrpyt')
    print('3: CSV')
    print('4: All')
    print('5: Exit')
    # print(os.environ)
    print(os.getenv('home') )
    # os.getenv('home') 
    option = int(input("Enter your option: "))
    if(option > 0 and option <6):
        autoGUI(option)
    else:
        exit() 

autoGUI_main()
