import { useCallback, useEffect, useState } from "react";
import { answerReview, listDueReviews, type ReviewItem } from "@/api/p2";
import { Button } from "@/components/ui/button";
import { ErrorText } from "@/components/ui/field";
import { useRouter } from "@/lib/router";

const RATINGS = ["忘记", "模糊", "掌握", "非常熟练"];

export function ReviewsPage() {
  const { navigate } = useRouter();
  const [reviews, setReviews] = useState<ReviewItem[]>([]);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      setReviews(await listDueReviews());
    } catch (e) {
      setError(e instanceof Error ? e.message : "加载失败");
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const answer = async (review: ReviewItem, rating: string) => {
    try {
      await answerReview(review.id, rating);
      void load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "提交失败");
    }
  };

  return (
    <main className="mx-auto w-full max-w-3xl space-y-6 px-6 py-10">
      <h1 className="text-2xl font-semibold tracking-tight">复习计划</h1>
      <ErrorText message={error} />
      {reviews.length === 0 ? (
        <p className="text-muted-foreground">今天没有到期的复习任务</p>
      ) : (
        <ul className="space-y-3">
          {reviews.map((review) => (
            <li key={review.id} className="rounded-lg border bg-card p-4 text-card-foreground shadow-sm">
              <button
                type="button"
                className="text-left font-medium"
                onClick={() => navigate(`/topics/${review.topic_id}`)}
              >
                {review.topic_name}
              </button>
              <div className="mt-2 flex flex-wrap gap-2">
                {RATINGS.map((rating) => (
                  <Button key={rating} variant="outline" size="sm" onClick={() => void answer(review, rating)}>
                    {rating}
                  </Button>
                ))}
              </div>
            </li>
          ))}
        </ul>
      )}
    </main>
  );
}
