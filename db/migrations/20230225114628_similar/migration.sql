-- CreateTable
CREATE TABLE "_similar" (
    "A" INTEGER NOT NULL,
    "B" INTEGER NOT NULL
);

-- CreateIndex
CREATE UNIQUE INDEX "_similar_AB_unique" ON "_similar"("A", "B");

-- CreateIndex
CREATE INDEX "_similar_B_index" ON "_similar"("B");

-- AddForeignKey
ALTER TABLE "_similar" ADD CONSTRAINT "_similar_A_fkey" FOREIGN KEY ("A") REFERENCES "NewsArticles"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "_similar" ADD CONSTRAINT "_similar_B_fkey" FOREIGN KEY ("B") REFERENCES "NewsArticles"("id") ON DELETE CASCADE ON UPDATE CASCADE;
