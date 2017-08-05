from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

drive = None

def insert_file(contra_cheque, file):

    if drive is None:
        _auth()

    #Realiza o upload
    upload = drive.CreateFile()
    file_name = get_file_name(contra_cheque)
    upload['title'] = file_name
    file_path = file["path"]
    upload.SetContentFile(file_path)
    upload.Upload()

    #Adiciona permissões públicas ao arquivo
    permission = upload.InsertPermission({
        'type': 'anyone',
        'value': 'anyone',
        'role': 'reader'})

    #Seta a url pública
    contra_cheque.url = upload['alternateLink']

def delete_file(contra_cheque):
    if drive is None:
        _auth()
    query = r"'root' in parents and trashed=false and name = '{}' ".format(get_file_name(contra_cheque))
    files = drive.ListFile({'q': query })
    for file in files:
        file.Trash()


def _auth():

    gauth = GoogleAuth()

    gauth.LoadCredentialsFile("mycreds.txt")
    if gauth.credentials is None:
        # Authenticate if they're not there
        gauth.LocalWebserverAuth()
    elif gauth.access_token_expired:
        # Refresh them if expired
        gauth.Refresh()
    else:
        # Initialize the saved creds
        gauth.Authorize()
    # Save the current credentials to a file
    gauth.SaveCredentialsFile("mycreds.txt")

    global drive
    drive = GoogleDrive(gauth)


def get_file_name(contra_cheque):
    return '{}-{}-{}/{}.pdf'.format(contra_cheque.matricula.orgao.sigla, contra_cheque.matricula.numero, contra_cheque.mes, contra_cheque.exercicio)