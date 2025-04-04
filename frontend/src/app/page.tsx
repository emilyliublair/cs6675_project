import { Plus } from "lucide-react";

export default function Home() {
  return (
    <div className="max-w-4xl mx-auto">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-800">Recent Questions</h1>
        <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 hover:cursor-pointer flex items-center space-x-2">
          <Plus className="" /> <span>New Question</span>
        </button>
      </div>

      <div className="space-y-4"></div>
    </div>
  );
}
