import { useEffect } from "react";
import ChatInputBox from "../component/ChatInputBox";
import { getCookie } from "../js/Methods"
import { useChatContext } from "../context/ChatContextProvider";

export default function NewChat() {
    const {deleteNewChatMsg, updateMsgList} = useChatContext()
    
    useEffect(() => {
        deleteNewChatMsg()
        updateMsgList([])
    }, [])

    return (
        <div className="relative"> 
            <div className="mt-[8vw] w-[100%] text-wrap">
                <p className="text-[4vw] whitespace-pre-line font-[600] gradient-text">
                    {`Hello, ${getCookie("username")}.\nHow can we help you?`}
                </p>
                <p className="text-[1.3vw] w-[60%] text-light-gray">
                    {"Any questions are welcome! However, questions regarding diabetes are recommended."}
                </p>
            </div>
            <div className="mt-[8vw]">
                <ChatInputBox chat_id={0} isLoading={null} setIsLoading={null}/>
            </div>
        </div>
    )
}
