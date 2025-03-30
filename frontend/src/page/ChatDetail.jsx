import { useEffect, useRef, useState } from "react"
import { useParams } from "react-router-dom"
import { useNavigate } from "react-router-dom"
import { useChatContext } from "../context/ChatContextProvider"
import { getCookie } from "../js/Methods"
import ChatInputBox from "../component/ChatInputBox"
import UserMsg from "../component/UserMsg"
import AiReply from "../component/AiReply"

const API = "http://localhost:8000/chats"
export default function ChatDetail() {
    const messageEnd = useRef()
    const navigate = useNavigate()
    const { id } = useParams()
    const [isLoading, setIsLoading] = useState(false)
    const {chatState, updateMsgList, addMsg, deleteNewChatMsg} = useChatContext()

    useEffect(() => {
        messageEnd.current?.scrollIntoView({ behavior: "smooth" })
    }, [chatState, isLoading])

    useEffect(() => {
        if ( !id ) {
            navigate("../newchat")
        }
        
        if (chatState.new_chat_msg.chat_id === Number(id) || chatState.new_chat_msg.msg_content !== "") {
            setIsLoading(true)
            const newMsg = {
                username: getCookie("username"),
                chat_id: Number(id),
                message_content: chatState.new_chat_msg.msg_content
            }

            fetch(`${API}/new-message`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(newMsg)
            }).then(response => {
                if (response.status === 200) {
                    return response.json()
                }

                return Promise.reject()
            }).then(data => {
                deleteNewChatMsg()
                addMsg(data)
            }).catch(response => {
                console.log(response)
            }).finally(() => {
                setIsLoading(false)
            })
            
        } else {
            fetch(`${API}/get-chat-detail?username=${getCookie("username")}&chat_id=${id}`).then(
                response => {
                    if (response.status === 200) {
                        return response.json()
                    }

                    return Promise.reject(response)
                }
            ).then(data => {
                data.sort((a, b) => ((a.date_added < b.date_added) ? -1 : ((a.date_added > b.date_added) ? 1 : 0)))
                updateMsgList(data)
            }).catch(response => {
                console.log(response)
            }).finally(() => {
                
            })
        }   
    }, [id])

    return(
        <div className="h-[100vh] flex flex-col">
            <div className="px-[2vw] w-full h-[80%] max-h-[80%] overflow-y-scroll scrollbar">
                {chatState.msg_list.map((msg, index) => {
                    if (msg.sender === "user") {
                        return <UserMsg key={index} message={msg.message_content} />
                    } else if (msg.sender === "ai") {
                        return <AiReply key={index} reply={msg.message_content} />
                    } else {
                        return <></>
                    }
                })}
                {isLoading && (
                    <div className="w-full h-fit flex flex-row text-[1.5vw] items-center gap-[0.5vw] font-[600] text-gray loader">
                        <div>Generating message</div>
                        <div className="w-[0.6vw] h-[0.6vw] rounded-3xl bg-gray dot"></div>
                        <div className="w-[0.6vw] h-[0.6vw] rounded-3xl bg-gray dot"></div>
                        <div className="w-[0.6vw] h-[0.6vw] rounded-3xl bg-gray dot"></div>
                    </div>
                )}
                <div className="w-full h-1"
                    ref={messageEnd}></div>
                
            </div>
            
            <div className="w-full h-fit">
                <ChatInputBox chat_id={id} setIsLoading={setIsLoading}/>
            </div>
        </div>
    )
}