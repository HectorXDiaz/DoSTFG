from .constants import COLUMNS, FIRST_ROW, COLUMN_ORDER
import pickle
import pandas as pd

class ModelProcessor:
    def __init__(self, influxdb_connector, line):
        self.influxdb_connector = influxdb_connector
        self.line = line

    def _process_line(self,):
        dataset = [FIRST_ROW.split(',')]
        dataset.append(self.line.split(','))
        df = pd.DataFrame(dataset[1:], columns=dataset[0])

        self.src_ip=df['src_ip'].iloc[0]
        self.dst_ip=df['dst_ip'].iloc[0]

        df = df.drop(columns=['src_port', 'dst_port', 'timestamp'])
        df = df.rename(COLUMNS, axis=1)
        df = df[COLUMN_ORDER]

        return df

    def process_model(self):
 
        df = self._process_line()
        with open('source/model/classification_tree.pkl', 'rb') as file:
            classifier_tree = pickle.load(file)
        new_predictions = classifier_tree.predict(df)
        print(new_predictions)

        point = self.influxdb_connector.point(int(new_predictions[0]),self.src_ip,self.dst_ip)
        self.influxdb_connector.write(point)
