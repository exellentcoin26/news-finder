/*
  Warnings:

  - You are about to drop the `_similar` table. If the table is not empty, all the data it contains will be lost.

*/
-- DropForeignKey
ALTER TABLE "_similar" DROP CONSTRAINT "_similar_A_fkey";

-- DropForeignKey
ALTER TABLE "_similar" DROP CONSTRAINT "_similar_B_fkey";

-- DropTable
DROP TABLE "_similar";

-- CreateTable
CREATE TABLE "SimilarArticles" (
    "id1" INTEGER NOT NULL,
    "id2" INTEGER NOT NULL,

    CONSTRAINT "SimilarArticles_pkey" PRIMARY KEY ("id1","id2")
);

-- AddForeignKey
ALTER TABLE "SimilarArticles" ADD CONSTRAINT "SimilarArticles_id1_fkey" FOREIGN KEY ("id1") REFERENCES "NewsArticles"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "SimilarArticles" ADD CONSTRAINT "SimilarArticles_id2_fkey" FOREIGN KEY ("id2") REFERENCES "NewsArticles"("id") ON DELETE CASCADE ON UPDATE CASCADE;
