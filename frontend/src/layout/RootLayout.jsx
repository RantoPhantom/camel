import { useState } from "react"
import Navbar from "../component/Navbar"
import { Outlet } from "react-router-dom"
import NavBarExtended from "../component/NavBarExtended"
import ChatContextProvider from "../context/ChatContextProvider"

export default function RootLayout() {
    const [isOpen, setIsOpen] = useState(false)

    return (
        <div className="flex flex-row w-full min-h-[100vh] bg-black">
            <ChatContextProvider>
                <div className="h-[100vh] fixed top-0 left-0 w-[5.3vw] bg-dark-gray">
                    <Navbar setIsOpen={setIsOpen}/>
                </div>
                <div className="text-white ml-[5.3vw] flex-1 box-border px-[10vw]">
                    <Outlet />
                </div>

                {isOpen && (
                    <div className="w-[100%] h-[100%] absolute bg-black-overlay"
                        onClick={() => setIsOpen(false)}>
                        <NavBarExtended setIsOpen={setIsOpen} />
                    </div>
                )}
            </ChatContextProvider>
            
        </div>
    )
}