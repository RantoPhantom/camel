import { useNavigate, useLocation } from 'react-router-dom'

export default function Navbar({setIsOpen}) {
    const navigate = useNavigate()
    const location = useLocation()

    function newChatHandler(event) {
        event.stopPropagation()
        if (location.pathname !== "./chat/newchat") {
            navigate("./newchat")

            return
        }

        return
    }

    return (
        <nav className="h-full flex flex-col justify-between cursor-pointer"
            onClick={() => setIsOpen(true)}>
            <div className="w-fit mx-auto mt-[0.5vw]">
                <i className="p-[0.3vw] ri-add-fill gradient text-white text-[2.8vw] rounded-lg cursor-pointer"
                    onClick={(e) => newChatHandler(e)}/>
                <div className="mx-auto h-[0.3vw] w-[3.5vw] m-[0.5vw] bg-gray" />
                <i className="ri-search-line text-gray text-[3vw] self-center"></i>
            </div>
            <div className="w-fit mx-auto flex flex-col gap-[1vw]">
                <i className="ri-user-line text-[3vw] text-gray"></i>
                <i className="ri-logout-box-line text-[3vw] text-gray"></i>
            </div>
        </nav>
    )
}