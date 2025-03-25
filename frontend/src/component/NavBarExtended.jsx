

export default function NavBarExtended() {

    return (
        <div className="h-[100%] w-[22%] bg-dark-gray p-[1vw] flex flex-col"
            onClick={(e) => e.stopPropagation()}>

            <div className="w-[100%] h-[3.3vw] gradient text-[1.3vw] rounded-lg flex justify-center items-center text-white font-[600]">
                New Chat
            </div>
            <div className="w-full h-[0.3vw] my-[1vw] bg-gray" />
            <input className="w-full h-[3.1vw] bg-dim-gray rounded-lg text-input px-[0.5vw] text-[1.1vw] text-white" placeholder="Search" />
            <div className="w-full flex-1 max-h-[55%] mt-[1.5vw] text-white font-[500] text-[1.2vw] overflow-y-scroll scrollbar-hidden">
                <div className="w-full h-fit bg-gray px-[0.8vw] py-[0.8vw] my-[0.5vw] rounded-lg">
                    Lorem ipsum dolor sit amet 
                </div>
                <div className="w-full h-fit bg-gray px-[0.8vw] py-[0.8vw] my-[0.5vw] rounded-lg">
                    Lorem ipsum dolor sit amet 
                </div>
                <div className="w-full h-fit bg-gray px-[0.8vw] py-[0.8vw] my-[0.5vw] rounded-lg">
                    Lorem ipsum dolor sit amet 
                </div>
                <div className="w-full h-fit bg-gray px-[0.8vw] py-[0.8vw] my-[0.5vw] rounded-lg">
                    Lorem ipsum dolor sit amet 
                </div>
                <div className="w-full h-fit bg-gray px-[0.8vw] py-[0.8vw] my-[0.5vw] rounded-lg">
                    Lorem ipsum dolor sit amet 
                </div>
                <div className="w-full h-fit bg-gray px-[0.8vw] py-[0.8vw] my-[0.5vw] rounded-lg">
                    Lorem ipsum dolor sit amet 
                </div>
                <div className="w-full h-fit bg-gray px-[0.8vw] py-[0.8vw] my-[0.5vw] rounded-lg">
                    Lorem ipsum dolor sit amet 
                </div>
                
                <div className="w-full h-fit bg-gray px-[0.8vw] py-[0.8vw] my-[0.5vw] rounded-lg">
                    Lorem ipsum dolor sit amet 
                </div>
                <div className="w-full h-fit bg-gray px-[0.8vw] py-[0.8vw] my-[0.5vw] rounded-lg">
                    Lorem ipsum dolor sit amet 
                </div>
                <div className="w-full h-fit bg-gray px-[0.8vw] py-[0.8vw] my-[0.5vw] rounded-lg">
                    Lorem ipsum dolor sit amet 
                </div>
                <div className="w-full h-fit bg-gray px-[0.8vw] py-[0.8vw] my-[0.5vw] rounded-lg">
                    Lorem ipsum dolor sit amet 
                </div>
            </div>

            <div className="flex flex-col gap-[1vw] mt-auto">
                <div className="w-full h-[0.3vw] bg-gray" />
                <div className="w-full h-fit text-[1.3vw] text-white flex flex-col">
                    <p><b>Username:</b> Anle</p>
                    <p><b>Role:</b> User</p>
                </div>
                <div className="w-full h-[0.3vw] bg-gray" />
                <div className="w-[100%] h-[3.3vw] bg-red-600 text-[1.3vw] rounded-lg flex justify-center items-center text-white font-[600]">
                    Log Out
                </div>
            </div>
            
            
        </div>
    )
}