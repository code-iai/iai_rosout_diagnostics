#!/usr/bin/env python

import rospy

from rosgraph_msgs.msg import Log
from diagnostic_msgs.msg import DiagnosticArray
from diagnostic_msgs.msg import DiagnosticStatus
from diagnostic_msgs.msg import KeyValue


class RosoutDiagnostics(object):

    def __init__(self):
        """
        Initialisation of a RosoutDiagnostics object.
        """

        self.sub = rospy.Subscriber("rosout_agg", Log, self.update)
        self.pub = rospy.Publisher("diagnostics", DiagnosticArray,  queue_size=10)
        self.level_mapping = {
            Log.INFO: DiagnosticStatus.OK,
            Log.DEBUG: DiagnosticStatus.OK,
            Log.WARN: DiagnosticStatus.WARN,
            Log.ERROR: DiagnosticStatus.ERROR,
            Log.FATAL: DiagnosticStatus.ERROR}

    def to_diagnostics_msg(self, msg):
        """
        Converts a rosout message into a diagnostics message.
        :param msg: rosout message to convert.
        :type msg: Log
        :return: New diagnostics message.
        :rtype: DiagnosticArray
        """
        level = self.level_mapping[msg.level]
        name = msg.name
        message = msg.msg
        hardware_id = msg.name
        values = [KeyValue('file', msg.file),
                  KeyValue('function', msg.function),
                  KeyValue('line', '{}'.format(msg.line))]

        status_array = [DiagnosticStatus(level, name, message, hardware_id, values)]
        msg.header.frame_id = rospy.get_name()
        return DiagnosticArray(msg.header, status_array)

    def update(self, msg):
        """
        Callback to process incoming rosout message. Will relate a corresponding message to diagnostics.
        :param msg: The rosout message to process.
        :type msg: rosout
        :return: None
        """
        if msg.name != rospy.get_name():
            self.pub.publish(self.to_diagnostics_msg(msg))


if __name__ == '__main__':
    rospy.init_node('rosout_diagnostics', anonymous=True)
    RosoutDiagnostics()
    rospy.spin()
