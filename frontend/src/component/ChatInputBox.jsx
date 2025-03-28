import { useState } from "react"
import { useChatContext } from "../context/ChatContextProvider"
import { getCookie } from "../js/Methods"
import { useLocation, useNavigate } from "react-router-dom"

const API = "http://localhost:8000"

export default function ChatInputBox({chat_id}) {
    const location = useLocation()
    const navigate = useNavigate()
    const {addMsg} = useChatContext()
    const [inputMsg, setInputMsg] = useState("")
    const {newChatMsg} = useChatContext()


    function onChangeHandler(event) {
        setInputMsg(event.target.value)
    }

    function onMessageSentHandler(event) {
        if (location.pathname === "/chat/newchat") {
            onNewChatMessageSent(event)
        } 

        if (location.pathname === `/chat/chatdetail/${chat_id}`) {
            onMessageSent(event)
        } 
        
        return
    }

    function onMessageSent(event) {
        event.preventDefault()
        const newMsg = {
            username: getCookie("username"),
            chat_id: Number(chat_id),
            message_content: inputMsg
        }

        fetch(`${API}/chats/new-message`, {
            method: "PUT",
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(newMsg)
        }).then(response => {
            if (response.status === 200) {
                return response.json()
            }

            return Promise.reject(response)
        }).then(data => {
            addMsg(data)
            setInputMsg("")
        }).catch(response => {
            console.log(response)
        })


    }

    function onNewChatMessageSent(event) {
        event.preventDefault()
        const newChat = {
            username: getCookie("username"),
            message: inputMsg
        }

        fetch(`${API}/chats/new-chat`, {
            method: "PUT",
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(newChat)
        }).then(response => {
            if (response.status === 200) {
                return response.json()
            }

            return Promise.reject()
        }).then(data => {
            console.log(data)
            const newCtxChat = {
                chat_id: data,
                msg_content: inputMsg
            }
            newChatMsg(newCtxChat)
            navigate(`../chatdetail/${data}`)

        }).catch(response => {
            console.log(response)
        })
    }

    return (
        <div className={`w-[100%] ${(location.pathname === "/chat/newchat") ? "h-[13vw]" : "h-[10vw]"}  bg-dark-gray rounded-2xl box-border px-[1.5vw] pt-[1vw] pb-[0.5vw] flex flex-col`}>
            <textarea className={`w-[100%] ${(location.pathname === "/chat/newchat") ? "h-[70%]" : "h-[60%]"} bg-dark-gray resize-none scrollbar text-input text-[1.3vw]`} placeholder="Ask something..."
                name="input_msg"
                value={inputMsg}
                onChange={(e) => onChangeHandler(e)}>
            </textarea>
            <div className="w-[100%] h-[0.15vw] bg-gray"/>
            <div className="w-[100%] flex-1 flex flex-row-reverse justify-between">
                <div className="w-[10%] my-[0.5vw] gradient rounded-lg relative cursor-pointer"
                    onClick={(e) => onMessageSentHandler(e)}>
                    <i className="ri-arrow-right-line text-white text-[1.8vw] absolute top-[50%] left-[50%] translate-x-[-50%] translate-y-[-50%]"></i>
                </div>
            </div>
        </div>
    )
}