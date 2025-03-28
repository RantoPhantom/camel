import { createContext, useContext, useReducer } from 'react'

const ChatContext = createContext(null);

export function useChatContext() {
    const chatCtx = useContext(ChatContext)

    if (chatCtx === null) {
        throw new Error("chatContext is null")
    }

    return chatCtx;
}

function chatReducer(state, action) {
    if (action.type === 'UPDATE_MSGLIST') {
        return {
            ...state,
            msg_list: action.payload
        }
    }

    if (action.type === 'ADD_MSG') {
        return {
            ...state,
            msg_list: [
                ...state.msg_list,
                ...action.payload
            ]
        }
    }

    if (action.type === 'DELETE_MSG') {
        let newState = state

        return newState.filter(msg => msg.message_id === action.payload)
    }

    if (action.type === 'NEW_CHAT_MSG') {
        return {
            ...state,
            new_chat_msg: action.payload
        }
    }

    if (action.type === 'REMOVE_NEW_CHAT_MSG') {
        return {
            ...state,
            new_chat_msg: {
                chat_id: null,
                msg_content: ""
            }
        }
    }


}

export default function ChatContextProvider({children}) {
    const [chatState, dispatch] = useReducer(chatReducer, {
        new_chat_msg: {
            chat_id: null,
            msg_content: ""
        },
        msg_list: []
    })

    const ctx = {
        chatState: chatState,
        updateMsgList(newMsgList) {
            dispatch({
                type: 'UPDATE_MSGLIST',
                payload: newMsgList
            })
        },
        addMsg(msg) {
            dispatch({
                type: 'ADD_MSG',
                payload: msg
            })
        },
        deleteMsg(msg_id) {
            dispatch({
                type: 'DELETE_MSG',
                payload: msg_id
            })
        },
        newChatMsg(msg) {
            dispatch({
                type: 'NEW_CHAT_MSG',
                payload: msg
            })
        },
        deleteNewChatMsg() {
            dispatch({
                type: 'REMOVE_NEW_CHAT_MSG'
            })
        }
    }

    return (
        <ChatContext.Provider value={ctx}>
            {children}
        </ChatContext.Provider>
    )
}