import { useLocation, useNavigate } from "react-router-dom"


export default function Chat({chat, setIsOpen}) {
    const navigate = useNavigate()
    const location = useLocation()

    function chatSelectHandler(event) {
        if (location.pathname !== `/chat/chatdetail/${chat.chat_id}`) {
            navigate(`./chatdetail/${chat.chat_id}`)
        }

        // setIsOpen(false)
    }

    return (
        <div className={`w-full h-fit ${location.pathname === `/chat/chatdetail/${chat.chat_id}` ? 'bg-light-gray' : 'bg-gray'} px-[0.8vw] py-[0.8vw] my-[0.5vw] rounded-lg cursor-pointer`}
            onClick={(e) => chatSelectHandler(e)}>
            {(chat.title.length === 20) ? `${chat.title}...`: chat.title}
        </div>
    )
}