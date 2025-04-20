import { FileText } from "lucide-react";

interface RelevantDocumentsProps {
  documents: string[];
}

export default function RelevantDocuments({ documents }: RelevantDocumentsProps) {
  if (!documents || documents.length === 0) {
    return null;
  }

  return (
    <div className="mt-4 border-t border-gray-200 pt-4">
      <h4 className="text-sm font-semibold text-gray-700 mb-2 flex items-center">
        <FileText className="w-4 h-4 mr-2" />
        Relevant Documents
      </h4>
      <div className="space-y-3">
        {documents.slice(0,5).map((doc, index) => (
          <div
            key={index}
            className="bg-gray-50 p-3 rounded-lg text-sm text-gray-600"
          >
            <div className="font-medium text-gray-700 mb-1">
              Document {index + 1}
            </div>
            <div className="whitespace-pre-wrap">{doc}</div>
          </div>
        ))}
      </div>
    </div>
  );
} 