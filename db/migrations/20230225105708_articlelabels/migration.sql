-- DropForeignKey
ALTER TABLE "NewsArticles" DROP CONSTRAINT "NewsArticles_source_id_fkey";

-- CreateTable
CREATE TABLE "NewsArticleLabels" (
    "id" INTEGER NOT NULL,
    "label" TEXT NOT NULL,

    CONSTRAINT "NewsArticleLabels_pkey" PRIMARY KEY ("id","label")
);

-- AddForeignKey
ALTER TABLE "NewsArticles" ADD CONSTRAINT "NewsArticles_source_id_fkey" FOREIGN KEY ("source_id") REFERENCES "NewsSources"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "NewsArticleLabels" ADD CONSTRAINT "NewsArticleLabels_id_fkey" FOREIGN KEY ("id") REFERENCES "NewsArticles"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "NewsArticleLabels" ADD CONSTRAINT "NewsArticleLabels_label_fkey" FOREIGN KEY ("label") REFERENCES "Labels"("name") ON DELETE CASCADE ON UPDATE CASCADE;
