import { Answer } from "@/@types/type";
import { ThumbsDown, ThumbsUp, Edit2, Save, X } from "lucide-react";
import { useState } from "react";

export default function TeacherAnswerCard({ answer }: { answer: Answer }) {
  const [upvotes, setUpvotes] = useState<number>(answer.upvotes || 0);
  const [downvotes, setDownvotes] = useState<number>(answer.downvotes || 0);
  const [hasVoted, setHasVoted] = useState<boolean>(false);
  const [isEditing, setIsEditing] = useState<boolean>(false);
  const [editedDescription, setEditedDescription] = useState<string>(answer.description);

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

  const handleEdit = async () => {
    try {
      const response = await fetch(`http://localhost:8001/answer/${answer._id}/edit`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          description: editedDescription,
          editedBy: "Teacher"
        }),
      });

      if (response.ok) {
        setIsEditing(false);
        // Update the answer object with the new description
        answer.description = editedDescription;
        answer.edited = true;
        answer.editedBy = "Teacher";
        answer.editDate = new Date().toISOString();
      }
    } catch (error) {
      console.error('Error editing answer:', error);
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
          <div className="flex justify-between items-center mb-1">
            <h3 className="text-lg font-semibold text-gray-800">Answer</h3>
            {!isEditing ? (
              <button
                onClick={() => setIsEditing(true)}
                className="text-blue-600 hover:text-blue-800 flex items-center space-x-1"
              >
                <Edit2 className="w-4 h-4" />
                <span>Edit</span>
              </button>
            ) : (
              <div className="flex space-x-2">
                <button
                  onClick={handleEdit}
                  className="text-green-600 hover:text-green-800 flex items-center space-x-1"
                >
                  <Save className="w-4 h-4" />
                  <span>Save</span>
                </button>
                <button
                  onClick={() => {
                    setIsEditing(false);
                    setEditedDescription(answer.description);
                  }}
                  className="text-red-600 hover:text-red-800 flex items-center space-x-1"
                >
                  <X className="w-4 h-4" />
                  <span>Cancel</span>
                </button>
              </div>
            )}
          </div>

          {isEditing ? (
            <textarea
              value={editedDescription}
              onChange={(e) => setEditedDescription(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent min-h-[150px]"
            />
          ) : (
            <p className="text-gray-600 mb-2">{answer.description}</p>
          )}

          <div className="flex items-center justify-between">
            <div className="flex items-center text-sm text-gray-500">
              <span className="font-medium text-gray-700">
                AI-generated answer
                {answer.edited && (
                  <span className="ml-2 text-blue-600">
                    (Edited by {answer.editedBy} on {new Date(answer.editDate || '').toLocaleDateString()})
                  </span>
                )}
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
        </div>
      </div>
    </div>
  );
} 