import { Answer } from "@/@types/type";
import { ThumbsDown, ThumbsUp } from "lucide-react";
import { useState } from "react";
import RelevantDocuments from "./RelevantDocuments";

export default function AnswerCard({ answer }: { answer: Answer }) {
  const [upvotes, setUpvotes] = useState<number>(answer.upvotes || 0);
  const [downvotes, setDownvotes] = useState<number>(answer.downvotes || 0);
  const [hasVoted, setHasVoted] = useState<boolean>(false);

  const handleVote = async (type: 'upvote' | 'downvote') => {
    if (hasVoted) return;

    try {
      const response = await fetch(`http://localhost:8001/answer/${answer._id}/${type}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        if (type === 'upvote') {
          setUpvotes((prev: number) => prev + 1);
        } else {
          setDownvotes((prev: number) => prev + 1);
        }
        setHasVoted(true);
      }
    } catch (error) {
      console.error('Error voting:', error);
    }
  };

  return (
    <div className="card mb-4">
      <div className="flex items-start space-x-4">
        <div className="flex-shrink-0">
          <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center">
            <span className="text-blue-600 font-semibold">A</span>
          </div>
        </div>

        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-800 mb-1">Answer</h3>
          <p className="text-gray-600 mb-2">{answer.description}</p>

          <div className="flex items-center justify-between">
            <div className="flex items-center text-sm text-gray-500">
              <span className="font-medium text-gray-700">
                AI-generated answer
              </span>
            </div>
            
            <div className="flex items-center space-x-4">
              <button
                onClick={() => handleVote('upvote')}
                disabled={hasVoted}
                className={`flex items-center space-x-1 ${
                  hasVoted ? 'opacity-50 cursor-not-allowed' : 'hover:text-green-600'
                }`}
              >
                <ThumbsUp className="hover:cursor-pointer "/>
                <span>{upvotes}</span>
              </button>

              <button
                onClick={() => handleVote('downvote')}
                disabled={hasVoted}
                className={`flex items-center space-x-1 ${
                  hasVoted ? 'opacity-50 cursor-not-allowed' : 'hover:text-red-600'
                }`}
              >
                <ThumbsDown className="hover:cursor-pointer "/>
                <span>{downvotes}</span>
              </button>
            </div>
          </div>
          {
          answer.relevant_documents && (
            <RelevantDocuments documents={answer.relevant_documents} />
          )}
        </div>
      </div>
    </div>
  );
}
