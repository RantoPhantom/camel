import { useState } from "react"
import Navbar from "../component/Navbar"
import { Outlet } from "react-router-dom"
import NavBarExtended from "../component/NavBarExtended"

export default function RootLayout() {
    const [isOpen, setIsOpen] = useState(false)

    return (
        <div className="flex flex-row w-[100vw] min-h-[100vh] bg-black">
            <div className="h-[100vh] fixed top-0 left-0 w-[5.3vw] bg-dark-gray">
                <Navbar setIsOpen={setIsOpen}/>
            </div>
            <div className="text-white flex-1 box-border px-[15vw]">
                <Outlet />
            </div>

            {isOpen && (
                <div className="w-[100%] h-[100%] absolute bg-black-overlay"
                    onClick={() => setIsOpen(false)}>
                    <NavBarExtended />
                </div>
            )}
        </div>
    )
}