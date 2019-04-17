# -*- coding: utf-8 -*-

LOCAL = 'local'
USER = 'user'

class DriveModeSelector:

    def run(self, user_mode, \
        user_left_value, user_left_status, \
        user_right_value, user_right_status, \
        user_lift_value, user_lift_status, \
        local_left_value, local_left_status, \
        local_right_value, local_right_status, \
        local_lift_value, local_lift_status):

        eval_value = lambda val: 0 if val is None else val
        eval_status = lambda stat: stat if stat in ['move', 'free', 'brake'] else 'free'

        if user_mode == LOCAL:
            return eval_value(local_left_value), eval_status(local_left_status), \
                eval_value(local_right_value), eval_status(local_right_status), \
                eval_value(local_lift_value), eval_status(local_lift_status)

        # user/mode値が未登録の場合もuser値を採用する
        return eval_value(user_left_value), eval_status(user_left_status), \
            eval_value(user_right_value), eval_status(user_right_status), \
            eval_value(user_lift_value), eval_status(user_lift_status)

    def shutdown(self):
        pass
