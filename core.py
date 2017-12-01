import xmlrpc.client
import csv
import pandas as pd

KEY = 'ae065052714284ef5ad6a2a77ef3f765'

HOST = 'http://allpositions.ru/api/'

class CookiesTransport(xmlrpc.client.Transport):
    def send_headers(self, connection, headers):
        connection.putheader("Cookie", 'api_key='+KEY+'; ')
        super().send_headers(connection, headers)

client = xmlrpc.client.ServerProxy(HOST, CookiesTransport())

def getPositions(pID, date):
    positions = pd.DataFrame(proxy.get_report(pID, date)['positions'], index=None).transpose()
    positions = positions.rename_axis('ids')
    positions = positions.reset_index()
    positions[['id_engine', 'id_query']] = positions['ids'].str.split('_', expand=True).astype(int)
    del positions['ids'], positions['change_position'], positions['prev_position']

    queries = pd.DataFrame(proxy.get_report(pID, date)['queries']).transpose()
    queries['id_query'] = queries['id_query'].astype(int)

    data = queries.set_index('id_query').join(positions.set_index('id_query'))
    data['date'] = date

    data = data.replace(to_replace=[1102885, 1102886], value=['Yandex', 'Google'])

    return data


def concatenateFiles(*args):
    result = pd.concat(*args, ignore_index=True, names=[0])

    return result


with client as proxy:
    #print(pd.DataFrame(proxy.get_projects(8381)))
    pID = 462066
    curent_date = '2017-06-15'
    #print(pd.DataFrame(proxy.get_report(pID, '2017-11-30')))

    data = getPositions(pID, curent_date)

    data2 = pd.read_excel('output.xlsx')

    frames = [data, data2]

    data3 = concatenateFiles(frames)


    writer = pd.ExcelWriter('output.xlsx')
    data3.to_excel(writer, 'Sheet2')
    writer.save()