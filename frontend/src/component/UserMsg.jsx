

export default function UserMsg({message}) {

    return(
        <div className="flex flex-row-reverse my-[0.5vw]">
            <p className="w-fit max-w-[35vw] p-[0.8vw] rounded-2xl bg-dark-gray font-[500] text-[1.1vw] text-justify">{message}</p>
        </div>
    )
}