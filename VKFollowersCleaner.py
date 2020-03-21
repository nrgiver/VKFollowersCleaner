import sys
import time
import datetime
import vk_api
import getpass

# VK Config
VK_login = ""
VK_password = ""
VK_version = 5.103
VK_application_id = 7363571
VK_scope = 2


def VK_auth2():
    return (input('Auth2 code (VK or SMS): '), False)


def VK_auth():
    while True:
        try:
            VK_login_local = VK_login
            VK_password_local = VK_password
            if len(VK_login_local) == 0:
                VK_login_local = input('Your login or phone: ')
            if len(VK_password_local) == 0:
                VK_password_local = getpass.getpass()
            vk_session = vk_api.VkApi(
                login=VK_login_local,
                password=VK_password_local,
                auth_handler=VK_auth2,
                app_id=VK_application_id,
                scope=VK_scope
            )
            vk_session.auth()
            return vk_session.get_api()
        except Exception as e: 
            print('Error: ' + str(e))
# VK Config

# Script Config
followers_count_add = 500  #Less then 500
blacklist_count_add = 200  #Less then 200
vk_execute_limit = 10  #Less then 25
# Script Config


def print_help():
    print(
        "VKFollowersCleaner.py <flags>\r\n\r\n" +
        "Flags:\r\n" +
        " -g Get deactivated followers and save in file\r\n" +
        " -c Clear your VK account by deactivated followers\r\n" +
        " -b Ban all deactivated followers by your VK account\r\n" +
        " -u Clear all users from your blacklist\r\n" +
        " -e This flag is optional for -c, -b, -u. This forces a method to use API.Execute instead of queries in loop\r\n\r\n" +
        "Examples:\r\n" +
        " VKFollowersCleaner.py -g (Output list of deactivated followers)\r\n" +
        " VKFollowersCleaner.py -b (Ban all deactivated followers using queries in loop)\r\n" +
        " VKFollowersCleaner.py -c -e (Clear all deactivated followers using API.Execute)" 
    )


def get_followers():
    vk = VK_auth()
    statistic_banned = 0
    statistic_deleted = 0
    statistic_other = 0
    followers_count_all = vk.users.getFollowers(count=0, v=VK_version)['count']
    followers_offset = 0
    timestamp = datetime.datetime.now()
    file_name = (
        "vk_deactivated_followers_" + str(timestamp.year) +
        str(timestamp.month) + str(timestamp.day) + "_" +
        str(timestamp.hour) + str(timestamp.minute) +
        str(timestamp.second) + str(timestamp.microsecond) + ".txt"
    )
    file = open(file_name, "w+")
    print("Start!")
    for followers_offset in range(0, followers_count_all, followers_count_add):
        print(
            "Progress: " + str(followers_offset) +
            " / " + str(followers_count_all)
        )
        followers = vk.users.getFollowers(
            fields='domain',
            offset=followers_offset,
            count=followers_count_add,
            v=VK_version
        )['items']
        for follower in followers:
            if 'deactivated' in follower:
                if follower['deactivated'] == 'banned':
                    statistic_banned += 1
                elif follower['deactivated'] == 'deleted':
                    statistic_deleted += 1
                else:
                    statistic_other += 1
                file.write(
                    str(follower['id']) + ": " +
                    str(follower['deactivated']) + "\r\n"
                )
    file.close()
    print(
        "Finish!\r\n\r\n"
        "Banned: " + str(statistic_banned) + "\r\n" +
        "Deleted: " + str(statistic_deleted) + "\r\n" +
        "Other: " + str(statistic_other) + "\r\n\r\n" +
        "List deactivated followers were save to the file '" +
        str(file_name) + "'"
    )


def clear_blacklist_execute():
    vk = VK_auth()
    statistic_unban = 0
    blacklist_count_all = vk.account.getBanned(count=0, v=VK_version)['count']
    blacklist_offset = 0
    print("Start!")
    for blacklist_offset in range(0, blacklist_count_all, blacklist_count_add):
        print(
            "Progress: " + str(blacklist_offset) +
            " / " + str(blacklist_count_all)
        )
        blacklist_users = vk.account.getBanned(
            offset=blacklist_offset,
            count=blacklist_count_add,
            v=VK_version
        )['items']
        for slice_begin in range(0, len(blacklist_users), vk_execute_limit):
            try:
                query_code = (
                    "var userlist = " +
                    str(blacklist_users[slice_begin:slice_begin + vk_execute_limit]) +
                    ";" +
                    "var i = 0;" +
                    "while (i < userlist.length) {" +
                    "API.account.unban({\"owner_id\":userlist[i]});" +
                    "i = i + 1;" +
                    "};" +
                    "return i;"
                )
                response = vk.execute(code=str(query_code), v=VK_version)
                statistic_unban += int(response)
                print(
                    "     Unbanned: " + str(statistic_unban) +
                    " Response: " + str(response)
                )
            except Exception as e:
                print(
                    "Error! slice: " +
                    str(blacklist_users[slice_begin:slice_begin + vk_execute_limit]) +
                    " (" + str(e) + ")"
                )
    print("Finish!\r\n\r\nUnbanned:" + str(statistic_unban))


def clear_followers_execute(onlyBan=False):
    vk = VK_auth()
    statistic_deleted = 0
    followers_count_all = vk.users.getFollowers(count=0, v=VK_version)['count']
    followers_offset = 0
    print("Start!")
    for followers_offset in range(followers_offset, followers_count_all, followers_count_add):
        print(
            "Progress: " + str(followers_offset) +
            " / " + str(followers_count_all)
        )
        deactivated_followers = list(
            map(
                lambda x: x['id'],
                list(
                    filter(
                        lambda x: 'deactivated' in x,
                        vk.users.getFollowers(
                            fields='domain',
                            offset=followers_offset,
                            count=followers_count_add,
                            v=VK_version
                        )['items']
                    )
                )
            )
        )
        for slice_begin in range(0, len(deactivated_followers), vk_execute_limit):
            try:
                query_code = (
                    "var userlist = " +
                    str(deactivated_followers[slice_begin:slice_begin + vk_execute_limit]) +
                    ";" +
                    "var i = 0;" +
                    "while (i < userlist.length) {" +
                    "API.account.ban({\"owner_id\":userlist[i]});"
                )
                if not onlyBan:
                    query_code += "API.account.unban({\"owner_id\":userlist[i]});"
                query_code += (
                    "i = i + 1;" +
                    "};" +
                    "return i;"
                )
                response = vk.execute(code=str(query_code), v=VK_version)
                vk.execute(code=str(query_code), v=VK_version)
                statistic_deleted += int(response)
                print(
                    "     Deleted: " + str(statistic_deleted) +
                    " Response: " + str(response)
                )
            except Exception as e:
                print(
                    "Error! slice: " +
                    str(deactivated_followers[slice_begin:slice_begin + vk_execute_limit]) +
                    " (" + str(e) + ")"
                )
    print("Finish!\r\n\r\nDeleted:" + str(statistic_deleted))


def clear_blacklist():
    vk = VK_auth()
    statistic_unban = 0
    blacklist_count_all = vk.account.getBanned(count=0, v=VK_version)['count']
    blacklist_offset = 0
    print("Start!")
    for blacklist_offset in range(0, blacklist_count_all, blacklist_count_add):
        print(
            "Progress: " + str(blacklist_offset) +
            " / " + str(blacklist_count_all)
        )
        blacklist_users = vk.account.getBanned(
            offset=blacklist_offset,
            count=blacklist_count_add,
            v=VK_version
        )['items']
        for blacklist_user in blacklist_users:
            try:
                time.sleep(1)
                vk.account.unban(owner_id=int(blacklist_user), v=VK_version)
                statistic_unban += 1
            except Exception as e:
                print("Error! id: " + str(blacklist_user) + " (" + str(e) + ")")
    print("Finish!\r\n\r\nUnbanned:" + str(statistic_unban))


def clear_followers(onlyBan=False):
    vk = VK_auth()
    statistic_deleted = 0
    followers_count_all = vk.users.getFollowers(count=0, v=VK_version)['count']
    followers_offset = 0
    print("Start!")
    for followers_offset in range(0, followers_count_all, followers_count_add):
        print(
            "Progress: " + str(followers_offset) +
            " / " + str(followers_count_all)
        )
        followers = vk.users.getFollowers(
            fields='domain',
            offset=followers_offset,
            count=followers_count_add,
            v=VK_version
        )['items']
        for follower in followers:
            try:
                if 'deactivated' in follower:
                    time.sleep(1)
                    vk.account.ban(owner_id=int(follower['id']), v=VK_version)
                    if not onlyBan:
                        time.sleep(1)
                        vk.account.unban(owner_id=int(follower['id']), v=VK_version)
                    statistic_deleted += 1
            except Exception as e:
                print("Error! id: " + str(follower['id']) + " (" + str(e) + ")")
    print("Finish!\r\n\r\nDeleted:" + str(statistic_deleted))


def main(argv):
    arguments = argv
    need_print_help = True
    if '-g' in arguments:
        need_print_help = False
        get_followers()
    elif '-c' in arguments:
        need_print_help = False
        if '-e' in arguments:
            clear_followers_execute(onlyBan=False)
        else:
            clear_followers(onlyBan=False)
    elif '-b' in arguments:
        need_print_help = False
        if '-e' in arguments:
            clear_followers_execute(onlyBan=True)
        else:
            clear_followers(onlyBan=True)
    elif '-u' in arguments:
        need_print_help = False
        if '-e' in arguments:
            clear_blacklist_execute()
        else:
            clear_blacklist()
    if need_print_help:
        print_help()


if __name__ == "__main__":
    main(sys.argv[1:])
