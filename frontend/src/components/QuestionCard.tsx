import { Post } from "@/@types/type";

export default function QuestionCard({
  title,
  description,
  publishDate,
  name,
}: Post) {
  const formatDate = (date: Date) => {
    return new Date(date).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  return (
    <div
      className="card mb-4 hover:cursor-pointer"
    >
      <div className="flex items-start space-x-4">
        <div className="flex-shrink-0">
          <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center">
            <span className="text-blue-600 font-semibold">
              {name.charAt(0).toUpperCase()}
            </span>
          </div>
        </div>

        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-800 mb-1">{title}</h3>
          <p className="text-gray-600 mb-2">{description}</p>

          <div className="flex items-center text-sm text-gray-500">
            <span className="font-medium text-gray-700">{name}</span>
            <span className="mx-2">•</span>
            <span>{formatDate(new Date(publishDate))}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
