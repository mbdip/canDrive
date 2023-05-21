from can import Message

class MainTableData:
    def __init__(self, timestamp, ID, RTR, IDE, DLC, DATA_ARRAY):
        self.timestamp = timestamp
        self.ID = ID
        self.RTR = RTR
        self.IDE = IDE
        self.DLC = DLC
        self.DATA_ARRAY = DATA_ARRAY

    def getRowData(self):
        return [self.timestamp, self.ID, self.RTR, self.IDE, self.DLC, *self.DATA_ARRAY]


    @classmethod
    def fromMessage(cls, message):
        timestamp = str(message.timestamp)[:7]  # Truncate to desired precision
        if message.is_extended_id:
            ID = f"{message.arbitration_id:08x}"
        else:
            ID = f"{message.arbitration_id:04x}"
        RTR = "01" if message.is_remote_frame else "00"
        IDE = "01" if message.is_extended_id else "00"
        DLC = str("{:02X}".format(message.dlc))
        DATA_ARRAY = [f"{x:02x}" for x in message.data]
        return cls(timestamp, ID, RTR, IDE, DLC, DATA_ARRAY)



    @classmethod
    def fromRowData(cls, rowData):
        timestamp, ID, RTR, EXT, DLC = rowData[:5]
        DATA = rowData[5:]
        return cls(timestamp, ID, RTR, EXT, DLC, DATA)
    @classmethod
    def fromTxRowData(cls, rowData):
        ID, RTR, EXT = rowData[:3]
        DATA = MainTableData.expand_array(rowData[3])
        return cls(None, ID, RTR, EXT, None, DATA)

    @classmethod
    def expand_array(cls, array):
        expanded_array = []
        if len(array) > 2:
            expanded_array.extend([array[i:i + 2] for i in range(0, len(array), 2)])
        else:
            expanded_array.append(array)
        return expanded_array

    def toMessage(self):
        timestamp = float(self.timestamp) if self.timestamp is not None else 0.0
        is_extended_id = self.IDE == "01"
        # To exclude label
        self.ID = self.ID.split(' ')[0].strip()
        arbitration_id = int(self.ID, 16)
        is_remote_frame = self.RTR == "01"
        dlc = int(self.DLC) if self.DLC is not None else None

        data = [int(x, 16) for x in self.DATA_ARRAY]
        message = Message(timestamp=timestamp, arbitration_id=arbitration_id, is_extended_id=is_extended_id,
                              is_remote_frame=is_remote_frame, dlc=dlc, data=data)
        return message