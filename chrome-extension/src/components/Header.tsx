export default function Header({
    showClear,
    onClear,
}: {
    showClear: boolean;
    onClear?: () => void;
}) {
    return (
        <div className="flex justify-between items-center mb-4">
            <div className="text-xl font-bold">🎬 VidQuery</div>
            {showClear && (
                <button
                    onClick={onClear}
                    className="text-sm bg-red-600 hover:bg-red-700 text-white px-2 py-1 rounded"
                >
                    Clear
                </button>
            )}
        </div>
    );
}
