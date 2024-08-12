#TODO: enable to add items dinamically in the future
#id:    each account discord id
#owner: if you have two discord accounts, use same owner and you can share your configs, stats, etx
id2owner = {
    1234567890123456789: "OWNER_NAME0",
    9876543210987654321: "OWNER_NAME0",
    1111111111111111111: "OWNER_NAME1"
}

#TODO: enable to add items dinamically in the future
#owner: if you have two discord accounts, use same owner and you can share your configs, stats, etx
#id:    each account discord id
owner2id = {
    "OWNER_NAME0": [
        1234567890123456789,
        9876543210987654321
    ],
    "OWNER_NAME1":[
        1111111111111111111
    ]
}

#TODO: enable to add items dinamically in the future
#display name: your name in the server
id2dispname = {
    1234567890123456789: "DISPLAY_NAME0",
    9876543210987654321: "DISPLAY_NAME1",
    1111111111111111111: "DISPLAY_NAME2"
}

#TODO: enable to add items dinamically in the future
#return is_owner_joining_in_voice_chat
is_join_list = {
    "OWNER_NAME0": False,
    "OWNER_NAME1": False,
}

#the privileged user's id list
admin_ids=[
    1234567890123456789,
    9876543210987654321
]

#means the number of people in VoiceChannel
vcnum = 0