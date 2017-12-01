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


def get_dates():
    with client as proxy:
        base = pd.DataFrame(proxy.get_projects(8381)).transpose().set_index('url')['id_project']
        base = base.reset_index()

        dates_all = {}
        for ids in base['id_project']:
            dates = {}
            dates.update(proxy.get_report_dates(ids))
            for i in dates:
                dates[i] = str(ids) + '_' + dates[i]
            dates_all.update(dates)

        dates_all = pd.DataFrame.from_dict(dates_all, orient='index')
        dates_all['id_project'], dates_all['date'] = zip(*dates_all[0].map(lambda x: x.split('_')))
        del dates_all[0]

        return dates_all
