import { GraduationCap } from "lucide-react";
import Image from "next/image";
import Link from "next/link";

const Sidebar = () => {
  return (
    <div className="w-64 bg-white border-r border-gray-200 h-full">
      <div className="p-4">
        <h1 className="text-xl font-bold text-gray-800 mb-6">PiazzaHut</h1>
        <nav className="space-y-2">
          <Link
            href="/"
            className="flex items-center space-x-2 p-2 rounded-lg hover:bg-gray-100 text-gray-700"
          >
            <Image src={"/icons/home.svg"} alt="" height={24} width={24} />
            <span>Home</span>
          </Link>
          <Link
            href="/teacher"
            className="flex items-center space-x-2 p-2 rounded-lg hover:bg-gray-100 text-gray-700"
          >
            <GraduationCap />
            <span>Teacher View</span>
          </Link>
        </nav>
      </div>
    </div>
  );
};

export default Sidebar;
