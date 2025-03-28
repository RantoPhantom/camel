

export default function Login() {
    return (
        <div className="w-[100vw] h-[100vh] relative text-white">
            <div className="w-fit h-fit bg-dark-gray absolute top-1/2 left-1/2 translate-x-[-50%] translate-y-[-50%] rounded-lg box-border px-[2vw] py-[1vw] flex flex-col">
                <div className="text-[1.8vw] font-[600] mx-auto py-[0.8vw]">
                    Log In
                </div>
                <div className="flex flex-col gap-[0.5vw] mt-[1vw]">
                    <div className="text-[1.1vw] font-[500]">
                        Username:
                    </div>
                    <input type="text" className="text-[1.2vw] w-[22vw] py-[0.2vw] px-[0.5vw] bg-gray rounded-md text-input"></input>
                </div>
                <div className="flex flex-col gap-[0.5vw] mt-[1vw]">
                    <div className="text-[1.1vw] font-[500]">
                        Password:
                    </div>
                    <input type="text" className="text-[1.2vw] w-[22vw] py-[0.2vw] px-[0.5vw] bg-gray rounded-md text-input"></input>
                </div>
                <div className="flex justify-center mt-[1.5vw] text-[1vw]">
                    <p>Don't have an account? <a href="./signup" className="underline text-blue-300">Sign Up</a></p>
                </div>
                <div className="w-full gradient text-[1.5vw] font-[600] text-center mt-[5vw] py-[0.4vw] rounded-lg mb-[1vw]">
                    Log In
                </div>
            </div>
        </div>
    )
}